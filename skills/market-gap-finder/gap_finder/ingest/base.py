"""Adapter interface + the block-detector wrapper.

Codex C demoted "Block Detector" from a top-level component to a wrapper that
sits around fragile fetches — which is what this is. Every adapter implements
`Adapter`; fragile ones (Trustpilot) run their HTTP through `guarded_fetch`,
which turns an anti-bot response into a BLOCKED SourceResult (fail-closed) plus
a handoff record the human can act on, rather than a silent empty result.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import requests

from ..schema import Review, Source, SourceResult, FetchStatus


class Adapter(ABC):
    """One review source. Kept split per source: heterogeneous I/O, distinct
    failure modes, independently swappable (Codex C kept these separate)."""

    source: Source

    @abstractmethod
    def probe(self, product: str, hints: dict) -> Optional[dict]:
        """Cheap presence + volume check for the Worth-It Gate.
        Returns {"url": ..., "review_count": int, ...} if the product has a
        usable profile on this source, else None. No heavy pulling here."""

    @abstractmethod
    def pull(self, product: str, locator: dict, limit: int) -> SourceResult:
        """Fetch up to `limit` reviews for a product given the locator that
        `probe` resolved. Must return a SourceResult with an honest status."""


class BlockedError(Exception):
    """Raised inside a guarded fetch when anti-bot defences trip."""
    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"blocked at {url}: {reason}")


# Signals that a fetch was blocked rather than genuinely empty.
_BLOCK_STATUS = {403, 429, 503}
_BLOCK_MARKERS = (
    "captcha",
    "are you a robot",
    "cf-browser-verification",
    "attention required",   # Cloudflare
    "access denied",
)


def looks_blocked(resp: requests.Response) -> Optional[str]:
    """Return a reason string if the response looks like an anti-bot block,
    else None. Covers the silent block too: a 200 whose body is a challenge."""
    if resp.status_code in _BLOCK_STATUS:
        return f"HTTP {resp.status_code}"
    body = (resp.text or "").lower()
    for marker in _BLOCK_MARKERS:
        if marker in body:
            return f"challenge page ({marker})"
    return None


def guarded_fetch(url: str, *, session: requests.Session, timeout: int = 20,
                  **kwargs) -> requests.Response:
    """GET a URL and raise BlockedError if it looks blocked. Fragile adapters
    call this so a block becomes an explicit, catchable event."""
    resp = session.get(url, timeout=timeout, **kwargs)
    reason = looks_blocked(resp)
    if reason:
        raise BlockedError(url, reason)
    return resp


def blocked_result(product: str, source: Source, url: str, reason: str) -> SourceResult:
    """Build the fail-closed SourceResult for a blocked source. The CLI turns
    these into the human-handoff alert (open in a real logged-in browser)."""
    return SourceResult(
        product=product, source=source, status=FetchStatus.BLOCKED,
        reviews=[], url=url,
        note=f"BLOCKED ({reason}). Needs manual fetch — open {url} in a "
             f"logged-in browser and re-feed the page.",
    )
