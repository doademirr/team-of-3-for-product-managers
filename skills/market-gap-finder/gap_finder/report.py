"""Report — render the synthesis to a Markdown file.

Codex C: this is templating, so it's a renderer function, not a component.
Follows the competitive-landscape template (players / strengths / weaknesses /
gaps = differentiators). States the evidence caveat once: reviews are lagging,
self-selected sentiment (Tier ~2-3) — a proxy for opportunity, not proof of it.
"""

from __future__ import annotations

import datetime as _dt

_CAVEAT = (
    "> **How to read this.** These findings come from customer *reviews* — "
    "lagging, self-selected sentiment that over-represents the extremes "
    "(1★ and 5★). They tell you how existing products *fail*, which is a "
    "strong *proxy* for opportunity, not proof of it. Weight a gap by whether "
    "it is (a) frequent, (b) unserved by all players, and (c) something you "
    "could uniquely solve now."
)


def render(synthesis: dict, problem: str, anchor: str | None = None) -> str:
    out: list[str] = []
    out.append(f"# Market Gap Report — {problem}")
    out.append(f"*As of {_dt.date.today().isoformat()} · source: customer reviews*\n")
    if anchor:
        out.append(f"**Anchor:** {anchor} — the gaps below are where the field "
                   f"(including {anchor}) leaves customers unserved.\n")
    out.append(_CAVEAT + "\n")

    if synthesis.get("market_summary"):
        out.append("## Market summary\n")
        out.append(synthesis["market_summary"] + "\n")

    # --- The gold: gaps first ---
    gaps = synthesis.get("gaps", [])
    out.append("## Market gaps — the opportunity\n")
    if not gaps:
        out.append("_No cross-product gaps identified (insufficient review data)._\n")
    for i, g in enumerate(gaps, 1):
        affected = ", ".join(g.get("products_affected", [])) or "—"
        out.append(f"### {i}. {g.get('gap', 'Unnamed gap')}")
        out.append(f"- **Why it's an opportunity:** {g.get('why_opportunity', '—')}")
        out.append(f"- **Unserved by:** {g.get('unserved_by', '—')}")
        out.append(f"- **Seen in:** {affected}")
        out.append(f"- **Confidence:** {g.get('confidence', '—')}\n")

    # --- Per-product teardown ---
    out.append("## The players\n")
    anchor_key = (anchor or "").strip().lower()
    for p in synthesis.get("products", []):
        name = p.get("product", "Unknown")
        is_anchor = anchor_key and name.strip().lower() == anchor_key
        out.append(f"### {name}{'  ★ (anchor)' if is_anchor else ''}")
        cov = ", ".join(f"{k}: {v}" for k, v in (p.get("coverage") or {}).items())
        n = p.get("review_count")
        meta = f"*{n} reviews · {cov}*" if n else f"*{cov}*"
        out.append(meta)
        if p.get("incomplete"):
            out.append("_Incomplete — no reviews retrieved (source empty or blocked)._\n")
            continue
        out.append("\n**Loved:**")
        for love in p.get("loves", []) or ["_none surfaced_"]:
            out.append(_bullet(love, "theme"))
        out.append("\n**Complained about:**")
        for c in p.get("complaints", []) or ["_none surfaced_"]:
            out.append(_bullet(c, "theme", severity=True))
        out.append("")

    return "\n".join(out)


def _bullet(item, key: str, severity: bool = False) -> str:
    if isinstance(item, str):
        return f"- {item}"
    theme = item.get(key, "—")
    support = item.get("support", "")
    sev = f" _[{item.get('severity')}]_" if severity and item.get("severity") else ""
    quote = item.get("quote", "")
    tail = f" — {support}" if support else ""
    line = f"- **{theme}**{sev}{tail}"
    if quote:
        line += f'\n  > "{quote}"'
    return line
