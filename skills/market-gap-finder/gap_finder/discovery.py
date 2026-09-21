"""Discovery — identify the players AND resolve their review surfaces.

Codex C merged the old "Player Identifier" + "Surface Locator" here. Two jobs:

1. identify_players() — ask Claude, WITH LIVE WEB SEARCH, for the 5-8 products
   that solve the customer's problem (incl. indirect/adjacent). Web search
   matters: the whole tool is worthless if the players are hallucinated from
   stale training data.
2. resolve + gate — probe each adapter for each player. Resolution is the
   hallucination guard (a product that resolves to no store/subreddit/Trustpilot
   is dropped). The Worth-It Gate then turns a source OFF for the run unless
   enough players clear a review-count threshold on it (esp. Trustpilot).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .schema import Source
from .config import (DISCOVERY_MODEL, ANTHROPIC_API_KEY, settings,
                     REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
from .ingest.apple import AppleAdapter
from .ingest.google_play import GooglePlayAdapter
from .ingest.trustpilot import TrustpilotAdapter
from .ingest.reddit import RedditAdapter

_PROMPT = """\
You are a product-market researcher. The customer problem / niche is:

    {problem}

{seed_clause}Find the TOP products people actually use to solve this problem TODAY.
Use web search to ground every one in reality — do NOT rely on memory.

Include the real competitive set, not just obvious direct competitors:
- direct  — same job, same approach
- indirect — same job, different approach
- adjacent — solve a neighbouring part of the problem

Aim for 5-8 products. For each, give its primary consumer-facing web domain
(bare domain, e.g. "myfitnesspal.com") so its Trustpilot page can be found, and
whether it has consumer mobile apps.

After researching, output ONLY a JSON array (in a ```json fenced block), no prose:
[
  {{"name": "...", "category": "direct|indirect|adjacent",
    "why_relevant": "one line", "domain": "example.com",
    "has_mobile_app": true}}
]"""

_COMPANY_PROMPT = """\
You are a product-market researcher. The user wants to analyse this product /
company and see how competitors stack up against it:

    {company}

Use web search to ground every product in reality — do NOT rely on memory.

Return {company} ITSELF, plus the products that compete with it and adjacent
products solving the same customer job:
- direct  — same job, same approach
- indirect — same job, different approach
- adjacent — solve a neighbouring part of the problem

Aim for 5-8 products TOTAL, INCLUDING {company}. For each, give its primary
consumer-facing web domain (bare, e.g. "zoe.com") and whether it has consumer
mobile apps.

After researching, output ONLY a JSON array (in a ```json fenced block), no prose:
[
  {{"name": "...", "category": "direct|indirect|adjacent",
    "why_relevant": "one line", "domain": "example.com",
    "has_mobile_app": true}}
]"""


@dataclass
class Player:
    name: str
    category: str = "direct"
    why_relevant: str = ""
    domain: str | None = None
    has_mobile_app: bool = True
    is_anchor: bool = False        # the company the user asked to analyse


@dataclass
class DiscoveryResult:
    problem: str
    players: list[Player]                      # kept (resolved to >=1 source)
    dropped: list[str]                         # names dropped as unresolvable
    source_map: dict[str, dict]               # product -> {Source: locator}
    live_sources: list[Source]                # sources that cleared the gate
    notes: list[str] = field(default_factory=list)
    anchor: str | None = None                 # anchor company name, if any


# ---------------- player identification (LLM + web search) ----------------

def identify_players(problem: str | None = None,
                     seed_products: list[str] | None = None,
                     client=None, company: str | None = None) -> list[Player]:
    client = client or _default_client()
    if company:
        prompt = _COMPANY_PROMPT.format(company=company)
    else:
        seed_clause = ""
        if seed_products:
            seed_clause = ("Consider these as starting points but go beyond them: "
                           + ", ".join(seed_products) + ".\n\n")
        prompt = _PROMPT.format(problem=problem, seed_clause=seed_clause)
    text = _run_with_search(client, prompt)
    players = [_to_player(d) for d in _extract_json_array(text)]
    if company:
        players = _ensure_anchor(players, company)
    return players


def _norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())


def _ensure_anchor(players: list[Player], company: str) -> list[Player]:
    """Guarantee exactly one anchor, at the front (so max_players can't drop it).
    Exact (normalised) match only — substring matching would false-positive
    (fail-closed). If no player matches, inject the company as the anchor."""
    key = _norm(company)
    anchor: Player | None = None
    rest: list[Player] = []
    for p in players:
        if anchor is None and _norm(p.name) == key:
            p.is_anchor = True
            anchor = p
        else:
            p.is_anchor = False          # dedup: only one anchor
            rest.append(p)
    if anchor is None:
        anchor = Player(name=company, category="anchor",
                        why_relevant="(your anchor company)", is_anchor=True)
    return [anchor] + rest


def _default_client():
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set — add it to .env")
    import anthropic
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _run_with_search(client, prompt: str) -> str:
    """One create() call with web search, looping over pause_turn until the
    model finishes. Returns the concatenated final text."""
    tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": 6}]
    messages = [{"role": "user", "content": prompt}]
    resp = client.messages.create(
        model=DISCOVERY_MODEL, max_tokens=8000,
        thinking={"type": "adaptive"}, tools=tools, messages=messages,
    )
    guard = 0
    while getattr(resp, "stop_reason", None) == "pause_turn" and guard < 8:
        messages.append({"role": "assistant", "content": resp.content})
        resp = client.messages.create(
            model=DISCOVERY_MODEL, max_tokens=8000,
            thinking={"type": "adaptive"}, tools=tools, messages=messages,
        )
        guard += 1
    return _text_of(resp)


def _text_of(resp) -> str:
    parts = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts)


def _extract_json_array(text: str) -> list[dict]:
    """Tolerantly pull the JSON array out of the model's reply."""
    m = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    blob = m.group(1) if m else None
    if blob is None:
        m = re.search(r"(\[.*\])", text, re.DOTALL)  # bare array fallback
        blob = m.group(1) if m else None
    if not blob:
        return []
    try:
        data = json.loads(blob)
        return data if isinstance(data, list) else []
    except (ValueError, TypeError):
        return []


def _to_player(d: dict) -> Player:
    return Player(
        name=(d.get("name") or "").strip(),
        category=d.get("category", "direct"),
        why_relevant=d.get("why_relevant", ""),
        domain=(d.get("domain") or None),
        has_mobile_app=bool(d.get("has_mobile_app", True)),
    )


# ---------------- resolve sources + Worth-It Gate ----------------

def default_adapters() -> list:
    adapters = [AppleAdapter(), GooglePlayAdapter(), TrustpilotAdapter()]
    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:   # only if creds are configured
        adapters.append(RedditAdapter())
    return adapters


def discover(problem: str | None = None, seed_products: list[str] | None = None,
             client=None, adapters=None, company: str | None = None) -> DiscoveryResult:
    """Convenience: identify + resolve in one call (non-interactive path)."""
    players = identify_players(problem=problem, seed_products=seed_products,
                               client=client, company=company)
    context = problem or (f"{company} and its competitors" if company else "")
    return resolve(context, players, adapters=adapters,
                   anchor=(company or None))


def resolve(context: str, players: list[Player], adapters=None,
            anchor: str | None = None) -> DiscoveryResult:
    """Probe every (approved) player against every adapter, drop unresolvable
    ones, and run the Worth-It Gate. Runs AFTER the user approves the set."""
    players = [p for p in players if p.name][:settings.max_players]
    adapters = adapters if adapters is not None else default_adapters()

    source_map: dict[str, dict] = {}
    probe_errors: list[str] = []
    for p in players:
        locs = {}
        for ad in adapters:
            try:
                loc = ad.probe(p.name, hints={"domain": p.domain})
            except Exception as e:  # note it — a probe error is not "not present"
                probe_errors.append(f"{p.name}/{ad.source.value}: {type(e).__name__}")
                loc = None
            if loc:
                locs[ad.source] = loc
        source_map[p.name] = locs

    kept = [p for p in players if source_map.get(p.name)]
    dropped = [p.name for p in players if not source_map.get(p.name)]
    live = _worth_it_gate(source_map, kept)

    notes = []
    if probe_errors:
        notes.append("Probe errors (may hide a real source): " + "; ".join(probe_errors))
    if dropped:
        notes.append(f"Dropped (resolved to no source): {', '.join(dropped)}")
    for src in [Source.APPLE, Source.GOOGLE_PLAY, Source.TRUSTPILOT]:
        if src not in live:
            notes.append(f"{src.value} skipped — below Worth-It threshold "
                         f"({settings.worth_it_min_products} products × "
                         f"{settings.worth_it_min_reviews} reviews).")
    return DiscoveryResult(context, kept, dropped, source_map, live, notes,
                           anchor=anchor)


def _worth_it_gate(source_map: dict, players: list[Player]) -> list[Source]:
    """A source is live for the run only if at least worth_it_min_products
    players have at least worth_it_min_reviews on it."""
    live = []
    for src in [Source.APPLE, Source.GOOGLE_PLAY, Source.TRUSTPILOT, Source.REDDIT]:
        n = 0
        blocked = False
        for p in players:
            loc = source_map.get(p.name, {}).get(src)
            if not loc:
                continue
            if loc.get("blocked"):
                blocked = True   # couldn't measure — force a pull so the block surfaces
            if loc.get("review_count", 0) >= settings.worth_it_min_reviews:
                n += 1
        # A blocked probe must not silently drop the source: pull it so the
        # adapter fails closed to BLOCKED and the handoff fires (fail-closed).
        if n >= settings.worth_it_min_products or blocked:
            live.append(src)
    return live
