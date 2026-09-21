# Market Gap-Finder — Design

**What it is.** A tool for the Discovery / market-analysis stage of a 0→1 product.
Give it a customer problem or a company to anchor on; it finds the products solving
that problem (direct + indirect), pulls their customer reviews, and reports — per
product — what customers **love** and **complain about**, then aggregates the
complaints no one serves into **market gaps = candidate differentiators**.

**What it is NOT.** Not an ongoing competitor tracker. Reviews are lagging
sentiment about what exists; they won't tell you a competitor shipped a feature
last week.

## Architecture (4 modules)

Kept deliberately lean for a single-user tool — a design review flagged an earlier
6-component version as over-split.

1. **Discovery** (`discovery.py`) — two phases, so approval can sit between them:
   - `identify_players` — an LLM with live web search names 5–8 players. Two input
     modes: a **problem** statement, or `--company` (anchor mode: the company is
     always included — injected + flagged if the model omits it — and the set is
     its competitors).
   - **[approval checkpoint]** — the annotated set is shown; the user approves /
     drops / adds before anything is scraped.
   - `resolve` — probe each approved player's review surfaces. Resolution *is* the
     hallucination guard: a made-up product resolves to nothing and is dropped.
     Ends with the **Worth-It Gate** — a source is "live" only if enough products
     clear a review-count threshold (Trustpilot is skipped when not material).
2. **Ingestion** (`ingest/`) — four adapters behind one `Adapter` interface (Apple
   RSS, Google Play, Reddit/PRAW, Trustpilot HTML). Reddit "reviews" are relevant
   submissions + top comments. Fragile fetches run through **`guarded_fetch`** — a
   block-detector wrapper: 403/429, CAPTCHA/Cloudflare, or empty-when-expected →
   `BLOCKED` + a human-handoff note, never a silent empty.
3. **Cache** (`cache.py`) — raw reviews as JSON per (run, product, source). Runs
   are resumable; re-synthesis is free; the cache survives a synthesis failure.
4. **Synthesis + Report** (`synthesis.py` → `report.py`) — map-reduce LLM
   (per-product summary, then cross-product gaps), then a Markdown renderer. Hard
   rule: **never invent** a theme not in the reviews.

## Contracts (`schema.py`)

- `Review{source, product, text, rating?, date?, url?, source_metadata}` — one
  shape across all sources; source-specific fields live in `source_metadata` so
  they don't leak.
- `SourceResult{product, source, status, reviews, url, note}` with `FetchStatus` —
  **fail-closed**: `BLOCKED`/`EMPTY`/`NOT_PRESENT`/`ERROR`/`SKIPPED` are distinct
  from "no complaints".

## Failure modes (explicit)

- Discovery fails → stop the run.
- A source fails/blocks → mark it, degrade, keep going; the report says
  "incomplete". Fetch errors are `ERROR`, not `EMPTY`.
- Synthesis fails / returns unparseable output → flagged, cached reviews remain.

## Security posture

- **Prompt injection:** scraped review text reaches the model as UNTRUSTED DATA —
  delimited, with a system instruction to never follow instructions inside it.
- **Secrets:** only from `.env` (gitignored).
- **Strict parsing:** Trustpilot parsing accepts only genuine review cards, so
  arbitrary or manually-supplied HTML can't pose as reviews.
- **No unsafe auto-action:** only local writes + an explicit human handoff.
- **Accepted risk:** the Markdown report embeds model/review text unescaped —
  low impact for a local file; revisit if it's ever served.
