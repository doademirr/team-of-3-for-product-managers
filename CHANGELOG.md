# Changelog

Capability milestones for the Team-of-3 harness. Newest first.

## v1.6 — evals check
Added an Evals check as an always-on practice: before a product or major change reaches real users, test the whole product, including failure and safety cases, and report what isn't covered. The user sets the pass bar and signs off release.

## v1.5 — poke first and PRD unknowns
Added Poke first as an always-on practice: run a small sample of real or realistic data through the roughest working version, so you find out what you don't know. The PRD's open questions became an unknowns table that the user, Claude and the critic all add to, and the PRD ruler now checks it.

## v1.4 — first tool task (`market-gap-finder`)
Added a third task shape: a *tool* task, alongside the convergent and divergent generate→critique tasks. `market-gap-finder` is a real tool that discovers a niche's players, scrapes their customer reviews (App Store, Google Play, Reddit, Trustpilot), and reports the cross-product gaps no one serves. It lights up the Phase-1 Discovery "market analysis" stage in the locator. Because a tool carries its own quality gates (a worth-it source gate, never-invent synthesis, fail-closed handling, and the user's player-set approval), the locator routes it straight to the tool and **skips the critic loop** — a critique of the tool's *output* is a possible future upgrade, not part of this release.

## v1.3 — cross-session project memory
The harness remembers projects across sessions — one short file per project in `projects/`, read at the start (warm start / resume / route) and written back on task completion. Auto-resumes with a single project, asks which with several. State only; it does not track timelines.

## v1.2 — first divergent task (`prioritise-ideas`)
Added the divergent path. The critic judges the decision *frame* (completeness, evidence grounding, no strawmanned options, no free pass for the favourite, recommendation withheld) — never the choice itself. The frame is always handed back to the user; that escalation is the success state.

## v1.1 — stage locator + severity-gated cap
Step 0.5 locates where the user is in the 0→1 build and maps it to the wired task; unwired stages are named honestly rather than improvised. The loop cap became two blocks of three rounds, gated by severity: minor-only issues stop and summarise; a surviving moderate/critical checks in with the user before a second block, then escalates with a named cause.

## v1.0 — convergent harness + the critic seam
One shared loop, per-task rulers, structured verdicts (PASS / ISSUES / BLOCKED / UNABLE_TO_REVIEW), fail-closed on any seam failure. PM pack (`write-prd`, `write-user-stories`) and coding pack (`build-feature`). The critic seam (`critic.sh`) is the single model-invocation point — read-only sandbox, untrusted content delimited with a per-call nonce, output canonicalised against `verdict.schema.json`. Committed eval gate (`test-critic.sh`).
