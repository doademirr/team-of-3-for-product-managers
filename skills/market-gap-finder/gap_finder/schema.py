"""Data contracts shared across the pipeline.

One normalised Review shape spans four heterogeneous sources (Apple, Google
Play, Reddit, Trustpilot). Codex C flagged that source-specific fields would
otherwise leak, so anything that does not generalise lives in
`source_metadata`, and every fetch carries a `url` + the source's status.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional


class Source(str, Enum):
    APPLE = "apple_app_store"
    GOOGLE_PLAY = "google_play"
    REDDIT = "reddit"
    TRUSTPILOT = "trustpilot"


class FetchStatus(str, Enum):
    """Per (product, source) outcome. Fail-closed: a blocked or errored source
    is marked, never silently reported as 'no complaints'."""
    OK = "ok"                    # pulled successfully
    EMPTY = "empty"              # source exists but genuinely had no reviews
    NOT_PRESENT = "not_present"  # product has no profile on this source
    BLOCKED = "blocked"          # anti-bot / CAPTCHA / 403 — needs human assist
    ERROR = "error"              # unexpected failure
    SKIPPED = "skipped"          # worth-it gate turned this source off for the run


@dataclass
class Review:
    """One normalised customer review from any source."""
    source: Source
    product: str                 # canonical product name (from Discovery)
    text: str
    rating: Optional[float] = None   # 1-5 where the source has stars; None for Reddit
    date: Optional[str] = None       # ISO 8601 if known
    url: Optional[str] = None        # where it came from (traceability)
    source_metadata: dict[str, Any] = field(default_factory=dict)  # e.g. country, subreddit, upvotes

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["source"] = self.source.value
        return d


@dataclass
class SourceResult:
    """The outcome of pulling ONE source for ONE product. Carries the status so
    downstream synthesis knows the difference between 'no complaints' and
    'we couldn't get in'."""
    product: str
    source: Source
    status: FetchStatus
    reviews: list[Review] = field(default_factory=list)
    url: Optional[str] = None
    note: str = ""               # human-readable reason, esp. for BLOCKED/ERROR
