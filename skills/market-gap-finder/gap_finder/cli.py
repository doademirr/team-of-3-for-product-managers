"""CLI orchestrator — the one entrypoint that runs the pipeline:

    identify players -> [YOU approve the set] -> pull reviews -> cache
      -> synthesise -> report

Two input modes:
  python -m gap_finder.cli "tracking biological age at home"   # problem-first
  python -m gap_finder.cli --company "Zoe"                      # anchor a company

Company mode always includes that company and finds who competes with it, so the
report reads as "how the field stacks up against <company>". After identifying
the players (one cheap LLM step), it PAUSES and shows you the annotated set to
approve / trim / add — nothing is scraped until you say go. `--yes` skips the gate.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json

from . import discovery, cache, handoff, synthesis, report
from .config import settings
from .schema import FetchStatus


def _run_id(target: str) -> str:
    return f"{_dt.date.today().isoformat()}-{target[:40]}"


# ---------------- approval checkpoint (B + C) ----------------

def _print_players(players) -> None:
    print("\n  Proposed set for analysis:")
    for i, p in enumerate(players, 1):
        tag = "  ★anchor" if p.is_anchor else ""
        why = f" — {p.why_relevant}" if p.why_relevant else ""
        dom = f"  ({p.domain})" if p.domain else ""
        print(f"   {i}. {p.name} [{p.category}]{tag}{why}{dom}")


def _apply_edits(players, cmd):
    """Pure edit step (unit-tested). Returns (players, done)."""
    cmd = cmd.strip()
    if cmd == "":
        return players, True                       # Enter = proceed
    if cmd.startswith("+"):
        name = cmd[1:].strip()
        if name:
            players = players + [discovery.Player(
                name=name, category="user-added", why_relevant="(added by you)")]
        return players, False
    drops = {int(t) for t in cmd.split() if t.isdigit()}
    players = [p for i, p in enumerate(players, 1) if i not in drops]
    return players, False


def _player_to_dict(p) -> dict:
    return {"name": p.name, "category": p.category, "why_relevant": p.why_relevant,
            "domain": p.domain, "is_anchor": p.is_anchor}


def _players_json(players) -> str:
    """Machine-readable player list for the skill wrapper to show in chat
    (used by --list-only, so the approval can happen in conversation)."""
    return json.dumps([_player_to_dict(p) for p in players], indent=2, ensure_ascii=False)


def _load_players(path: str):
    """Load an approved player set (same shape as --list-only output)."""
    data = json.loads(open(path, encoding="utf-8").read())
    return [discovery.Player(
        name=d["name"], category=d.get("category", "direct"),
        why_relevant=d.get("why_relevant", ""), domain=d.get("domain"),
        is_anchor=bool(d.get("is_anchor", False))) for d in data]


def _confirm_players(players):
    while True:
        _print_players(players)
        try:
            cmd = input("\n  Proceed? [Enter=yes · drop e.g. '2 4' · "
                        "add '+Name' · 'q'=quit]: ").strip()
        except EOFError:
            # No interactive input and no --yes -> we CANNOT have approval, so
            # abort rather than scrape unapproved (fail-closed).
            print("\n  No input (non-interactive). Aborting — pass --yes to skip "
                  "the checkpoint.")
            return []
        if cmd.lower() in ("q", "quit"):
            return []
        if cmd and not cmd.startswith("+") and not any(t.isdigit() for t in cmd.split()):
            print("  (didn't recognise that — Enter to proceed, numbers to drop, "
                  "+Name to add, q to quit)")
            continue
        players, done = _apply_edits(players, cmd)
        if done:
            return players
        if not players:
            print("  (set is now empty — add one with +Name, or q to quit)")


# ---------------- pipeline ----------------

def run(problem: str | None = None, company: str | None = None,
        seed: list[str] | None = None, run_id: str | None = None,
        limit: int | None = None, assume_yes: bool = False,
        list_only: bool = False, players_file: str | None = None) -> None:
    target = company or problem
    run_id = run_id or _run_id(target)
    limit = limit or settings.reviews_per_source
    adapters = discovery.default_adapters()
    by_source = {a.source: a for a in adapters}
    context = problem or (f"{company} and its competitors" if company else target)

    if players_file:
        # Phase 2 of the skill flow: run with a set the user already approved.
        players = _load_players(players_file)
        print(f"\n▶ Using {len(players)} approved players from {players_file}")
    else:
        label = f"company: {company}" if company else f"problem: {problem}"
        print(f"\n▶ Discovering players ({label}) …")
        players = discovery.identify_players(problem=problem, company=company,
                                             seed_products=seed)
        if not players:
            print("  No players identified. Try a broader problem statement.")
            return
        if list_only:
            # Phase 1 of the skill flow: print the set for chat approval, stop.
            print(_players_json(players))
            return
        if not assume_yes:
            players = _confirm_players(players)
            if not players:
                print("  No players left — aborting.")
                return
    print("\n▶ Checking review sources for each player …")
    disc = discovery.resolve(context, players, adapters=adapters,
                             anchor=(company or None))
    for note in disc.notes:
        print(f"   – {note}")
    print(f"  Live sources this run: {[s.value for s in disc.live_sources] or 'none'}")

    # ---- ingest live sources for each player, cache each result ----
    print("\n▶ Pulling reviews …")
    results = []
    for p in disc.players:
        for source, locator in disc.source_map.get(p.name, {}).items():
            if source not in disc.live_sources:
                continue
            adapter = by_source.get(source)
            if adapter is None:
                continue
            res = adapter.pull(p.name, locator, limit)
            cache.save(run_id, res)
            results.append(res)
            flag = "" if res.status == FetchStatus.OK else f"  ({res.status.value})"
            print(f"   {p.name} · {source.value}: {len(res.reviews)} reviews{flag}")

    handoff.report_blocked(run_id, results)

    ok = sum(len(r.reviews) for r in results if r.status == FetchStatus.OK)
    print(f"\n✓ Ingestion done: {ok} reviews cached under data/{cache._slug(run_id)}/")
    if ok == 0:
        print("  No reviews retrieved — nothing to synthesise.")
        return

    print("\n▶ Synthesising loves / complaints / gaps …")
    result = synthesis.synthesise(results, context)
    md = report.render(result, context, anchor=disc.anchor)
    out_path = cache.run_dir(run_id) / "report.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"\n✓ Report written: {out_path}")
    print(f"  {len(result.get('gaps', []))} market gaps across "
          f"{len(result.get('products', []))} products.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Market Gap-Finder")
    parser.add_argument("problem", nargs="?", default=None,
                        help="the customer problem / niche to analyse")
    parser.add_argument("--company", default=None,
                        help="anchor a company: always included + its competitors found")
    parser.add_argument("--yes", action="store_true",
                        help="skip the approval checkpoint (for automation)")
    parser.add_argument("--list-only", action="store_true",
                        help="print the identified players as JSON and stop "
                             "(phase 1 of the skill flow; approve in chat)")
    parser.add_argument("--players-file", default=None,
                        help="run with an approved player set (JSON from --list-only)")
    parser.add_argument("--seed", nargs="*", default=None,
                        help="optional seed product names (problem mode)")
    parser.add_argument("--run-id", default=None,
                        help="name for this run's cache folder (default: date+target)")
    parser.add_argument("--limit", type=int, default=None,
                        help="max reviews per source (default from config)")
    args = parser.parse_args()
    if bool(args.problem) == bool(args.company):
        parser.error("give exactly one of: a problem statement, OR --company NAME")
    if args.company and args.seed:
        parser.error("--seed is for problem mode; omit it when using --company")
    run(args.problem, company=args.company, seed=args.seed,
        run_id=args.run_id, limit=args.limit, assume_yes=args.yes,
        list_only=args.list_only, players_file=args.players_file)


if __name__ == "__main__":
    main()
