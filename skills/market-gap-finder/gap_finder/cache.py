"""On-disk JSON cache of raw pulled reviews.

Keyed per (run, product, source) so a run is resumable and re-synthesis is
free — you never re-scrape to re-run the analysis. Codex C: on synthesis
failure the cache survives, so the expensive part isn't lost.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .schema import SourceResult, Review, Source, FetchStatus

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def run_dir(run_id: str) -> Path:
    d = DATA_DIR / _slug(run_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def save(run_id: str, result: SourceResult) -> Path:
    path = run_dir(run_id) / f"{_slug(result.product)}__{result.source.value}.json"
    payload = {
        "product": result.product,
        "source": result.source.value,
        "status": result.status.value,
        "url": result.url,
        "note": result.note,
        "reviews": [r.to_dict() for r in result.reviews],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path


def load(run_id: str, product: str, source: Source) -> SourceResult | None:
    path = run_dir(run_id) / f"{_slug(product)}__{source.value}.json"
    if not path.exists():
        return None
    raw = json.loads(path.read_text())
    reviews = [
        Review(source=Source(r["source"]), product=r["product"], text=r["text"],
               rating=r.get("rating"), date=r.get("date"), url=r.get("url"),
               source_metadata=r.get("source_metadata", {}))
        for r in raw.get("reviews", [])
    ]
    return SourceResult(
        product=raw["product"], source=Source(raw["source"]),
        status=FetchStatus(raw["status"]), reviews=reviews,
        url=raw.get("url"), note=raw.get("note", ""),
    )
