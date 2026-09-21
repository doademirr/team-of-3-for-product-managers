"""Trustpilot review adapter — the fragile one.

Trustpilot has no free API and actively blocks scrapers, so this adapter:
- runs every fetch through `guarded_fetch` (the block wrapper): a 403/429,
  CAPTCHA/Cloudflare challenge, or empty-when-expected -> BLOCKED, fail-closed.
- parses the page's embedded `__NEXT_DATA__` JSON (robust) rather than styled
  HTML divs (brittle), with a light HTML fallback.

Block -> human handoff: on BLOCKED, `pull` returns a SourceResult carrying the
URL + instructions. A human (or Claude driving a logged-in browser) fetches the
page(s); `pull_from_html` re-parses that HTML through the SAME parser. So a
blocked source is never silently empty — it's paused, flagged, and resumable.

Trustpilot is keyed by a company DOMAIN (e.g. www.myfitnesspal.com), which
Discovery resolves and passes in `hints["domain"]`.
"""

from __future__ import annotations

import json
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .base import (Adapter, guarded_fetch, BlockedError, blocked_result)
from ..schema import Review, Source, SourceResult, FetchStatus

_BASE = "https://www.trustpilot.com/review/{domain}"
_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
}
_MAX_PAGES = 20


class TrustpilotAdapter(Adapter):
    source = Source.TRUSTPILOT

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(_HEADERS)

    # ---- locate ----
    def probe(self, product: str, hints: dict) -> Optional[dict]:
        """Needs a domain (from Discovery). Verifies the profile exists and
        reads its total review count for the Worth-It Gate."""
        domain = hints.get("domain") or hints.get("trustpilot_domain")
        if not domain:
            return None
        url = _BASE.format(domain=domain)
        try:
            resp = guarded_fetch(url, session=self.session)
        except BlockedError:
            # Blocked at probe time: report as present-but-blocked so the gate
            # can still decide, and the handoff can kick in during pull.
            return {"domain": domain, "url": url, "review_count": 0,
                    "blocked": True}
        except requests.RequestException:
            return None
        data = _extract_next_data(resp.text)
        if data is None:
            return None  # no Trustpilot profile / unrecognised page
        count = _business_review_count(data)
        return {"domain": domain, "url": url, "review_count": count,
                "matched_name": _business_name(data) or product}

    # ---- pull (live) ----
    def pull(self, product: str, locator: dict, limit: int) -> SourceResult:
        domain = locator["domain"]
        expected = locator.get("review_count", 0)
        base_url = _BASE.format(domain=domain)
        reviews: list[Review] = []
        error_note = ""
        for page in range(1, _MAX_PAGES + 1):
            if len(reviews) >= limit:
                break
            url = base_url + (f"?page={page}" if page > 1 else "")
            try:
                resp = guarded_fetch(url, session=self.session)
            except BlockedError as b:
                if reviews:  # partial pull before the block — keep it, mark incomplete
                    return SourceResult(product, self.source, FetchStatus.BLOCKED,
                                        reviews=reviews, url=b.url,
                                        note=f"Blocked at page {page} ({b.reason}) "
                                             f"after {len(reviews)} reviews. "
                                             f"Manual fetch to complete.")
                return blocked_result(product, self.source, b.url, b.reason)
            except requests.RequestException as e:
                error_note = f"Network error at page {page}: {e}"
                break
            page_reviews = _reviews_from_html(product, resp.text)
            if not page_reviews:
                break
            reviews.extend(page_reviews)

        if not reviews:
            if error_note:
                status, note = FetchStatus.ERROR, error_note
            elif expected > 0:
                # Profile has reviews but we parsed none -> markup drift, NOT
                # "no complaints". Fail closed (fail-closed).
                status = FetchStatus.ERROR
                note = (f"Parsed 0 reviews though the profile lists ~{expected}. "
                        f"Likely Trustpilot markup drift — parser needs updating.")
            else:
                status, note = FetchStatus.EMPTY, "No Trustpilot reviews parsed."
            return SourceResult(product, self.source, status, url=base_url, note=note)
        return SourceResult(product, self.source, FetchStatus.OK,
                            reviews=reviews[:limit], url=base_url)

    # ---- pull (handoff completion) ----
    def pull_from_html(self, product: str, url: str,
                       html_pages: list[str], limit: int = 300) -> SourceResult:
        """Parse page HTML fetched MANUALLY (logged-in browser) after a block.
        Same parser as the live path."""
        reviews: list[Review] = []
        for html in html_pages:
            reviews.extend(_reviews_from_html(product, html))
            if len(reviews) >= limit:
                break
        if not reviews:
            return SourceResult(product, self.source, FetchStatus.EMPTY, url=url,
                                note="Manual HTML contained no parseable reviews.")
        return SourceResult(product, self.source, FetchStatus.OK,
                            reviews=reviews[:limit], url=url)


# ---------- parsing helpers (shared by live + handoff) ----------

def _extract_next_data(html: str) -> Optional[dict]:
    soup = BeautifulSoup(html, "lxml")
    tag = soup.find("script", id="__NEXT_DATA__")
    if not tag or not tag.string:
        return None
    try:
        return json.loads(tag.string)
    except (ValueError, TypeError):
        return None


def _page_props(data: dict) -> dict:
    return (data or {}).get("props", {}).get("pageProps", {})


def _business_name(data: dict) -> Optional[str]:
    bu = _page_props(data).get("businessUnit", {})
    return bu.get("displayName") or bu.get("identifyingName")


def _business_review_count(data: dict) -> int:
    bu = _page_props(data).get("businessUnit", {})
    n = bu.get("numberOfReviews")
    if isinstance(n, dict):                 # {"total": N, ...}
        n = n.get("total")
    try:
        return int(n or 0)
    except (TypeError, ValueError):
        return 0


def _reviews_from_html(product: str, html: str) -> list[Review]:
    """Primary: __NEXT_DATA__ JSON. Fallback: visible review cards."""
    data = _extract_next_data(html)
    if data is not None:
        raw = _page_props(data).get("reviews", []) or []
        out = [_json_review(product, r) for r in raw if (r or {}).get("text")]
        if out:
            return out
    return _html_fallback(product, html)


def _json_review(product: str, r: dict) -> Review:
    dates = r.get("dates", {}) or {}
    rating = r.get("rating")
    title = r.get("title") or ""
    text = r.get("text") or ""
    combined = f"{title}\n{text}".strip() if title else text
    return Review(
        source=Source.TRUSTPILOT, product=product, text=combined,
        rating=float(rating) if rating is not None else None,
        date=dates.get("publishedDate"),
        url=None,
        source_metadata={"likes": r.get("likes")},  # reviewer name omitted (privacy)
    )


def _html_fallback(product: str, html: str) -> list[Review]:
    """Fallback DOM parse if __NEXT_DATA__ is absent. Deliberately STRICT
    (security review): only genuine Trustpilot review cards, never loose <article>/<p>,
    so arbitrary or manually-supplied HTML can't be mistaken for reviews. If the
    markup has drifted past these selectors, this returns nothing and pull()
    fails closed to ERROR rather than inventing evidence."""
    soup = BeautifulSoup(html, "lxml")
    out: list[Review] = []
    cards = soup.select("[data-service-review-card-paper]")
    for card in cards:
        text_el = card.select_one("[data-service-review-text-typography]")
        if not text_el:
            continue
        rating = None
        rating_el = card.select_one("[data-service-review-rating]")
        if rating_el and rating_el.get("data-service-review-rating"):
            try:
                rating = float(rating_el["data-service-review-rating"])
            except (ValueError, TypeError):
                pass
        out.append(Review(source=Source.TRUSTPILOT, product=product,
                          text=text_el.get_text(strip=True), rating=rating,
                          source_metadata={"parsed_via": "html_fallback"}))
    return out
