"""Apple App Store review adapter.

Uses two public, keyless Apple endpoints:
- iTunes Search API -> resolve a product name to an app id + rating count
  (this is the presence + volume probe for the Worth-It Gate, and the
  hallucination guard: a made-up product resolves to nothing).
- The customer-reviews RSS-as-JSON feed -> up to ~500 most-recent reviews per
  country storefront, so we pull across several countries and merge.

Not fragile (no anti-bot), so plain requests — no block wrapper needed here.
"""

from __future__ import annotations

from typing import Optional

import requests

from .base import Adapter
from ..schema import Review, Source, SourceResult, FetchStatus
from ..config import settings

_SEARCH = "https://itunes.apple.com/search"
_REVIEWS = ("https://itunes.apple.com/{country}/rss/customerreviews/"
            "page={page}/id={app_id}/sortby=mostrecent/json")
_HEADERS = {"User-Agent": "market-gap-finder/0.1"}
_MAX_PAGES = 10  # Apple caps the feed at ~10 pages of 50


class AppleAdapter(Adapter):
    source = Source.APPLE

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(_HEADERS)

    def probe(self, product: str, hints: dict) -> Optional[dict]:
        """Resolve the product to the best-matching app in the primary
        storefront. Returns app id, review count, and store URL, or None."""
        country = settings.apple_countries[0]
        try:
            resp = self.session.get(
                _SEARCH,
                params={"term": product, "country": country,
                        "entity": "software", "limit": 3},
                timeout=20,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
        except (requests.RequestException, ValueError):
            return None
        if not results:
            return None
        top = results[0]
        return {
            "app_id": str(top["trackId"]),
            "matched_name": top.get("trackName", product),
            "review_count": int(top.get("userRatingCount", 0) or 0),
            "url": top.get("trackViewUrl"),
            "developer": top.get("artistName"),
        }

    def pull(self, product: str, locator: dict, limit: int) -> SourceResult:
        app_id = locator["app_id"]
        store_url = locator.get("url")
        reviews: list[Review] = []
        fetch_error = ""
        for country in settings.apple_countries:
            for page in range(1, _MAX_PAGES + 1):
                if len(reviews) >= limit:
                    break
                url = _REVIEWS.format(country=country, page=page, app_id=app_id)
                try:
                    resp = self.session.get(url, timeout=20)
                    resp.raise_for_status()
                    entries = resp.json().get("feed", {}).get("entry", [])
                except (requests.RequestException, ValueError) as e:
                    fetch_error = f"{type(e).__name__}: {e}"
                    break  # storefront/page unavailable — move to next country
                if isinstance(entries, dict):
                    entries = [entries]
                page_reviews = [e for e in entries if "im:rating" in e]
                if not page_reviews:
                    break  # first entry is app metadata; no reviews left
                for e in page_reviews:
                    reviews.append(self._to_review(product, country, e))
                    if len(reviews) >= limit:
                        break

        if not reviews:
            # A fetch failure with no reviews is ERROR, not EMPTY (fail closed).
            if fetch_error:
                return SourceResult(product, self.source, FetchStatus.ERROR,
                                    url=store_url,
                                    note=f"Apple feed fetch failed: {fetch_error}")
            return SourceResult(product, self.source, FetchStatus.EMPTY,
                                url=store_url,
                                note="No reviews returned from Apple feed.")
        return SourceResult(product, self.source, FetchStatus.OK,
                            reviews=reviews, url=store_url)

    @staticmethod
    def _to_review(product: str, country: str, e: dict) -> Review:
        def label(key: str) -> str:
            v = e.get(key)
            return v.get("label", "") if isinstance(v, dict) else ""

        title = label("title")
        body = label("content")
        text = f"{title}\n{body}".strip() if title else body
        rating = None
        try:
            rating = float(e["im:rating"]["label"])
        except (KeyError, TypeError, ValueError):
            pass
        return Review(
            source=Source.APPLE, product=product, text=text, rating=rating,
            date=label("updated") or None,
            url=label("id") or None,
            source_metadata={"country": country, "version": label("im:version")},
        )
