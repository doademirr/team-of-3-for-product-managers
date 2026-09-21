"""Human handoff for blocked sources — the "alert me, I'll assist" loop.

When a fragile adapter (Trustpilot) comes back BLOCKED, the run doesn't fail and
doesn't silently drop the source. Instead:
  1. `report_blocked` prints a clear console ALERT and writes `_handoff.json`
     into the run's cache dir, listing each blocked (product, source, url).
  2. You (or Claude driving your logged-in Chrome) open those URLs, save each
     page's HTML to a file.
  3. `complete_from_files` re-parses that saved HTML through the adapter's own
     `pull_from_html`, caches the result, and clears the handoff entry.

Kept as thin glue, not a pipeline stage (Codex C: the block logic is a wrapper).
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import SourceResult, FetchStatus, Source
from .cache import run_dir, save

_HANDOFF = "_handoff.json"


def report_blocked(run_id: str, results: list[SourceResult]) -> list[dict]:
    """Collect BLOCKED results, alert the human, and persist the to-do list.
    Returns the list of pending handoff entries (empty if none blocked)."""
    blocked = [r for r in results if r.status == FetchStatus.BLOCKED]
    entries = [{"product": r.product, "source": r.source.value,
                "url": r.url, "note": r.note} for r in blocked]
    path = run_dir(run_id) / _HANDOFF
    path.write_text(json.dumps(entries, indent=2, ensure_ascii=False))

    if entries:
        print("\n" + "=" * 64)
        print(f"  ⚠  {len(entries)} SOURCE(S) BLOCKED — manual assist needed")
        print("=" * 64)
        for i, e in enumerate(entries, 1):
            print(f"  {i}. {e['product']} · {e['source']}")
            print(f"     open in a logged-in browser: {e['url']}")
        print("  Save each page's HTML to a file, then complete via:")
        print("    handoff.complete_from_files(run_id, adapter, product, url, [html_path])")
        print("=" * 64 + "\n")
    return entries


def pending(run_id: str) -> list[dict]:
    path = run_dir(run_id) / _HANDOFF
    if not path.exists():
        return []
    return json.loads(path.read_text())


def complete_from_files(run_id: str, adapter, product: str, url: str,
                        html_paths: list[str], limit: int = 300) -> SourceResult:
    """Finish a blocked source from manually-saved HTML pages. Caches the
    result and removes the entry from the handoff list."""
    html_pages = [Path(p).read_text(encoding="utf-8", errors="ignore")
                  for p in html_paths]
    result = adapter.pull_from_html(product, url, html_pages, limit=limit)
    save(run_id, result)
    _clear_entry(run_id, product, adapter.source)
    return result


def _clear_entry(run_id: str, product: str, source: Source) -> None:
    remaining = [e for e in pending(run_id)
                 if not (e["product"] == product and e["source"] == source.value)]
    (run_dir(run_id) / _HANDOFF).write_text(
        json.dumps(remaining, indent=2, ensure_ascii=False))
