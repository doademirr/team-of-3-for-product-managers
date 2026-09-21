---
name: market-gap-finder
description: Market-gap analysis for the Discovery / market-analysis stage of a 0→1 product. Give it a customer problem OR a company to anchor on; it finds the top 5–8 products (direct + indirect), pulls their real customer reviews (App Store, Google Play, Reddit, Trustpilot), and reports per-product loves/complaints + the cross-product GAPS no one serves — the candidate differentiators. Wired into Team of 3 as the Phase-1 market-analysis tool. Use at the market/competitor-analysis stage, to find the gaps in a product space, or to ask "how do competitors stack up against <company>".
---

Run the Market Gap-Finder and present the gaps. This is the **market-analysis
tool of the Team of 3 harness** (Phase 1 — Discovery). It's a real tool, not a
generate→critique task: it has its own quality gates (worth-it source gate,
never-invent synthesis, fail-closed handling), so there is **no critic step** —
the tool's gates plus the PM's player-set approval are the quality bar.

**Location:** `skills/market-gap-finder/` (a Python app). **Keys:**
`ANTHROPIC_API_KEY` in its `.env` (synthesis); Reddit is included only if
`REDDIT_CLIENT_ID`/`SECRET` are set too. Apple / Google Play / Trustpilot need no
keys.

## Step 1 — Identify the players (cheap; no scraping yet)

Ask the PM for the input if not given: a **problem/niche** OR a **company to
anchor on**. Then run:

```
cd skills/market-gap-finder && source .venv/bin/activate && \
  python -m gap_finder.cli --company "<Company>" --list-only     # anchor mode
# or:
python -m gap_finder.cli "<problem statement>" --list-only        # problem mode
```

`--list-only` prints the identified players as JSON and stops (one LLM call with
web search — no reviews pulled yet).

## Step 2 — Show the set and get approval (the checkpoint)

Parse the JSON and show it as a numbered list — **name · category · one-line why ·
domain**, with the ★anchor marked. Ask the PM to approve, drop, or add. Apply the
edits. **Nothing is scraped until approved.**

## Step 3 — Run the analysis on the approved set

Write the approved list to a temp JSON file and run with `--players-file` (skips
re-identifying and the terminal checkpoint):

```
python -m gap_finder.cli --company "<Company>" \
  --players-file <approved.json> --run-id "<short-slug>"
```

Use the same `--company`/problem as Step 1 so the anchor + context carry through.
The tool probes sources, applies the Worth-It Gate, pulls reviews, synthesises,
and writes `data/<run>/report.md`.

## Step 4 — Handle any blocked sources

If the run prints a **BLOCKED** alert, a source (usually Trustpilot) hit anti-bot
defences. Open the blocked URL in a logged-in browser, save the page HTML, and
complete the handoff via `gap_finder.handoff.complete_from_files(...)`, then re-run
(the cache is reused). Never treat a blocked source as "no complaints".

## Step 5 — Present

- Read `data/<run>/report.md`; give the **gaps first**, then a one-line-per-player
  strength/weakness.
- State coverage honestly (sources live / skipped / blocked).
- Keep the evidence caveat in view: reviews are lagging, self-selected sentiment —
  a proxy for opportunity, not proof.
- **Next-stage nudge:** market analysis usually feeds a prioritisation step (which
  gap to build) or a PRD. Offer, don't assume.

## Rules

- **Never invent** a player, review, or complaint. The tool won't; don't add to it.
- **The player set is the PM's call** — always run Step 2; never skip to scraping.
- The tool is the engine; this skill is the launcher. Details: `README.md`,
  `DESIGN.md`.
