# Project memory — `projects/`

Cross-session state for product-development projects run through **`team-of-3`** (the end-to-end consultant). **One short file per project**, named `<project-slug>.md`, stored in this folder. The harness reads this directory at the start of a session (Step 0.4) and writes state back on task completion (Step 5).

**Keep every file terse.** Fields are labels, not prose. Log entries ≤ 1 line. Open items ≤ 1 line each. If a file starts reading like an essay, trim it — that's a bug, not a feature. This is a *state file*, not a document.

Copy the block below for a new project (delete this header from the copy):

---

```
# Project: <name>
Problem/goal: <one line — what this moves>
Stage: <current 0→1 stage> → next: <next stage>
Status: active | parked | done | experiment

## Artifacts
- <type>: <path> (<date>)

## Open items
- <one line — an unresolved escalation or pending decision>

## Log
- YYYY-MM-DD: <one line — what happened this session>
```
