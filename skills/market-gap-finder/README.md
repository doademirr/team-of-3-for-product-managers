# Market Gap-Finder

A tool that finds the gaps in a product market by reading real customer reviews.

**You give it:** a customer problem (e.g. *"tracking biological age at home"*), or
a company to anchor on (e.g. `--company "Zoe"`).

**It gives you:** a Markdown report — the top 5–8 products solving that problem
(direct *and* indirect), what customers love about each, what they consistently
complain about, and the complaints **no one is serving** — the candidate
differentiators. In company mode, the report frames everything as *how the field
stacks up against your anchor*.

It reads reviews from the App Store, Google Play, and — when it's worth it —
Trustpilot, plus Reddit discussion if you add Reddit API credentials. It does
*not* track what competitors do over time; that's a different tool.

This is the **market-analysis tool of the [Team of 3](../../README.md) harness**
(Phase 1 — Discovery). It's a *tool* task, not a generate→critique one: it has its
own quality gates, so it runs without the critic loop.

## Setup

```bash
cd skills/market-gap-finder
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # then add your keys
```

Keys (see `.env.example`): an **Anthropic API key** (for the analysis) and,
optionally, **Reddit app credentials** (to include Reddit). Apple, Google Play,
and Trustpilot need no keys.

## Run

```bash
# problem-first — analyse a whole space
python -m gap_finder.cli "tracking biological age at home"

# company-anchored — analyse a company AND how competitors stack up against it
python -m gap_finder.cli --company "Zoe"
```

After it identifies the players (one quick step), it **pauses and shows you the
proposed set** with a one-line description each. Approve (Enter), drop by number
(`2 4`), or add your own (`+Levels`) before anything is scraped. `--yes` skips the
checkpoint; `--list-only` prints the set as JSON and stops (used to drive approval
from another program). The report lands at `data/<run>/report.md`.

## How it works

`identify players → you approve → pull reviews → cache → synthesise → report`.
Four modules:

1. **Discovery** — an LLM with live web search names the players (grounded, not
   from memory), then resolves each to its review surfaces. Resolution is the
   hallucination guard: a made-up product resolves to nothing and is dropped. A
   **Worth-It Gate** turns a source off for the run unless enough products clear a
   review-count threshold (so it won't scrape Trustpilot for a space that isn't on
   it).
2. **Ingestion** — one adapter per source behind a common interface. Fragile
   fetches (Trustpilot) run through a block detector: on an anti-bot block the
   source is marked `BLOCKED` and a **human-handoff** kicks in (open the page in a
   logged-in browser, save the HTML, feed it back) — never a silent "no reviews".
3. **Synthesis** — map-reduce over the reviews (per-product loves/complaints, then
   cross-product gaps). It **never invents** a theme not present in the reviews;
   scraped text is treated as untrusted data.
4. **Report** — Markdown, gaps first.

## Honest limits

Reviews are **lagging, self-selected sentiment** — they over-represent the
extremes and tell you how existing products *fail*, which is a *proxy* for
opportunity, not proof of it. Weight a gap by whether it's frequent, unserved by
all players, and something you could uniquely solve now.

## A note on usage

This is a research tool for your own market analysis. It reads **public** reviews
at modest volume. Some sites' terms restrict automated access — use it
responsibly, respect each site's terms and rate limits, and don't redistribute the
raw data it collects. The Trustpilot adapter is deliberately gated and fails
closed for exactly this reason.

## Tests

```bash
PYTHONPATH=. python tests/test_offline.py     # offline unit tests (no network)
PYTHONPATH=. python tests/live_check.py "MyFitnessPal"   # live smoke test (network)
```

Design notes: `DESIGN.md`.
