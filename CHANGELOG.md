# Changelog

Capability milestones for the Team-of-3 harness. Newest first.

## v1.3 — cross-session project memory
The harness remembers projects across sessions — one short file per project in `projects/`, read at the start (warm start / resume / route) and written back on task completion. Auto-resumes with a single project, asks which with several. State only; it does not track timelines.

## v1.2 — first divergent task (`prioritise-ideas`)
Added the divergent path. The critic judges the decision *frame* (completeness, evidence grounding, no strawmanned options, no free pass for the favourite, recommendation withheld) — never the choice itself. The frame is always handed back to the user; that escalation is the success state.

## v1.1 — stage locator + severity-gated cap
Step 0.5 locates where the user is in the 0→1 build and maps it to the wired task; unwired stages are named honestly rather than improvised. The loop cap became two blocks of three rounds, gated by severity: minor-only issues stop and summarise; a surviving moderate/critical checks in with the user before a second block, then escalates with a named cause.

## v1.0 — convergent harness + the critic seam
One shared loop, per-task rulers, structured verdicts (PASS / ISSUES / BLOCKED / UNABLE_TO_REVIEW), fail-closed on any seam failure. PM pack (`write-prd`, `write-user-stories`) and coding pack (`build-feature`). The critic seam (`critic.sh`) is the single model-invocation point — read-only sandbox, untrusted content delimited with a per-call nonce, output canonicalised against `verdict.schema.json`. Committed eval gate (`test-critic.sh`).
