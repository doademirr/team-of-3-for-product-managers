"""Google Play review adapter.

Uses the keyless `google-play-scraper` library:
- search() -> resolve a product name to an appId (presence + hallucination guard)
- app() -> the app's total review count (volume, for the Worth-It Gate)
- reviews() -> most-recent reviews

Google has no official reviews API for arbitrary apps; this library scrapes the
Play endpoints. It's more robust than raw HTML but can still fail, so failures
are caught and reported honestly rather than swallowed.
"""

from __future__ import annotations

from typing import Optional

from google_play_scraper import search, app, reviews, Sort

from .base import Adapter
from ..schema import Review, Source, SourceResult, FetchStatus
from ..config import settings

_LANG = "en"


class GooglePlayAdapter(Adapter):
    source = Source.GOOGLE_PLAY

    def __init__(self) -> None:
        self.country = settings.primary_country

    def probe(self, product: str, hints: dict) -> Optional[dict]:
        try:
            hits = search(product, lang=_LANG, country=self.country, n_hits=3)
        except Exception:
            return None
        if not hits:
            return None
        top = hits[0]
        app_id = top.get("appId")
        if not app_id:
            return None
        review_count = 0
        try:
            review_count = int(app(app_id, lang=_LANG, country=self.country)
                               .get("reviews", 0) or 0)
        except Exception:
            pass  # search matched; count is a nice-to-have for the gate
        return {
            "app_id": app_id,
            "matched_name": top.get("title", product),
            "review_count": review_count,
            "url": f"https://play.google.com/store/apps/details?id={app_id}",
            "developer": top.get("developer"),
        }

    def pull(self, product: str, locator: dict, limit: int) -> SourceResult:
        app_id = locator["app_id"]
        store_url = locator.get("url")
        try:
            result, _token = reviews(
                app_id, lang=_LANG, country=self.country,
                sort=Sort.NEWEST, count=limit,
            )
        except Exception as exc:
            return SourceResult(product, self.source, FetchStatus.ERROR,
                                url=store_url,
                                note=f"Google Play pull failed: {exc}")
        out = [self._to_review(product, r) for r in result if r.get("content")]
        if not out:
            return SourceResult(product, self.source, FetchStatus.EMPTY,
                                url=store_url,
                                note="No reviews returned from Google Play.")
        return SourceResult(product, self.source, FetchStatus.OK,
                            reviews=out, url=store_url)

    @staticmethod
    def _to_review(product: str, r: dict) -> Review:
        at = r.get("at")
        rating = r.get("score")
        return Review(
            source=Source.GOOGLE_PLAY, product=product,
            text=r.get("content", ""),
            rating=float(rating) if rating is not None else None,
            date=at.isoformat() if hasattr(at, "isoformat") else None,
            url=None,
            source_metadata={
                "thumbs_up": r.get("thumbsUpCount"),
                "app_version": r.get("reviewCreatedVersion"),
            },
        )
