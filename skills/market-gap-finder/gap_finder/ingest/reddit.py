"""Reddit review adapter.

Reddit isn't a review site — but it's often the MOST honest source, because
people describe the *problem* and their real frustrations, not a star rating.
So "reviews" here are relevant submissions + their top comments.

Uses PRAW in read-only (app-only) mode: client id + secret + user agent, no user
login. Creds come from .env; without them the adapter isn't added to the run
(see discovery.default_adapters). Search volume (submissions + their comment
counts) feeds the Worth-It Gate.
"""

from __future__ import annotations

import datetime as _dt
from typing import Optional
from urllib.parse import quote

from .base import Adapter
from ..schema import Review, Source, SourceResult, FetchStatus
from ..config import (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)

_PROBE_LIMIT = 25
_COMMENTS_PER_POST = 3


class RedditAdapter(Adapter):
    source = Source.REDDIT

    def __init__(self, reddit=None) -> None:
        self._reddit_obj = reddit   # injectable for tests

    def _reddit(self):
        if self._reddit_obj is not None:
            return self._reddit_obj
        if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET):
            raise RuntimeError("Reddit creds not set — add REDDIT_CLIENT_ID/SECRET to .env")
        import praw
        self._reddit_obj = praw.Reddit(
            client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT, check_for_async=False,
        )
        return self._reddit_obj

    def probe(self, product: str, hints: dict) -> Optional[dict]:
        # Let access errors (bad creds, rate limit, network) propagate — discovery
        # records them as a visible probe error instead of a silent "not present"
        # (fail-closed). None means a genuine empty search.
        subs = list(self._reddit().subreddit("all").search(
            product, sort="relevance", limit=_PROBE_LIMIT))
        if not subs:
            return None
        # Volume = submissions + the discussion under them (comment counts).
        volume = len(subs) + sum(int(getattr(s, "num_comments", 0) or 0) for s in subs)
        return {"query": product, "review_count": volume,
                "n_submissions": len(subs),
                "url": f"https://www.reddit.com/search/?q={quote(product)}"}

    def pull(self, product: str, locator: dict, limit: int) -> SourceResult:
        query = locator["query"]
        search_url = locator.get("url")
        reviews: list[Review] = []
        try:
            subs = self._reddit().subreddit("all").search(
                query, sort="relevance", limit=40)
            for s in subs:
                if len(reviews) >= limit:
                    break
                reviews.append(self._submission_review(product, s))
                reviews.extend(self._comment_reviews(product, s, limit - len(reviews)))
        except Exception as e:
            if reviews:      # partial pull — keep it, mark incomplete
                return SourceResult(product, self.source, FetchStatus.OK,
                                    reviews=reviews[:limit], url=search_url,
                                    note=f"Partial (search interrupted: {e})")
            return SourceResult(product, self.source, FetchStatus.ERROR,
                                url=search_url, note=f"Reddit pull failed: {e}")
        if not reviews:
            return SourceResult(product, self.source, FetchStatus.EMPTY,
                                url=search_url, note="No Reddit discussion found.")
        return SourceResult(product, self.source, FetchStatus.OK,
                            reviews=reviews[:limit], url=search_url)

    # ---- mapping ----
    def _submission_review(self, product: str, s) -> Review:
        title = getattr(s, "title", "") or ""
        body = getattr(s, "selftext", "") or ""
        text = f"{title}\n{body}".strip()
        return Review(
            source=Source.REDDIT, product=product, text=text, rating=None,
            date=_iso(getattr(s, "created_utc", None)),
            url="https://www.reddit.com" + getattr(s, "permalink", ""),
            source_metadata={"subreddit": str(getattr(s, "subreddit", "")),
                             "score": getattr(s, "score", None), "type": "submission"},
        )

    def _comment_reviews(self, product: str, s, budget: int) -> list[Review]:
        if budget <= 0:
            return []
        out: list[Review] = []
        try:
            s.comments.replace_more(limit=0)
            for c in list(s.comments)[:_COMMENTS_PER_POST]:
                if len(out) >= budget:
                    break
                body = (getattr(c, "body", "") or "").strip()
                if not body:
                    continue
                out.append(Review(
                    source=Source.REDDIT, product=product, text=body, rating=None,
                    date=_iso(getattr(c, "created_utc", None)),
                    url=None,
                    source_metadata={"subreddit": str(getattr(s, "subreddit", "")),
                                     "score": getattr(c, "score", None),
                                     "type": "comment"}))
        except Exception:
            pass  # comments are a bonus; never fail the pull over them
        return out


def _iso(epoch) -> Optional[str]:
    if not epoch:
        return None
    try:
        return _dt.datetime.fromtimestamp(epoch, tz=_dt.timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return None
