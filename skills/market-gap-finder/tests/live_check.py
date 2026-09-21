"""Live smoke test — hits the REAL Apple + Google Play endpoints (no keys).

Run this on a machine with network to confirm the adapters pull real reviews:
    cd skills/market-gap-finder && source .venv/bin/activate
    PYTHONPATH=. python tests/live_check.py "MyFitnessPal"
"""

from __future__ import annotations

import sys

from gap_finder.ingest.apple import AppleAdapter
from gap_finder.ingest.google_play import GooglePlayAdapter

product = sys.argv[1] if len(sys.argv) > 1 else "MyFitnessPal"

for label, Adp in [("APPLE APP STORE", AppleAdapter), ("GOOGLE PLAY", GooglePlayAdapter)]:
    print(f"\n===== {label} : {product} =====")
    a = Adp()
    loc = a.probe(product, {})
    if not loc:
        print("  probe -> no match (product not found on this store, or network blocked)")
        continue
    print(f"  probe -> {loc['matched_name']}  |  ~{loc['review_count']:,} ratings  |  {loc['url']}")
    res = a.pull(product, loc, limit=10)
    print(f"  pull  -> status={res.status.value}  reviews={len(res.reviews)}")
    for r in res.reviews[:3]:
        snippet = (r.text or "").replace("\n", " ")[:100]
        print(f"     [{r.rating}] {snippet!r}")
