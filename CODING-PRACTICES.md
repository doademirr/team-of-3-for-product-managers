# Coding practices — the `build-feature` generator baseline

The `build-feature` task has no separate skill file; Claude writes/edits code following the practices below. These are also the source of the coding ruler's objective gate (Step 6C, half 1) and the security surface that decides whether a CODEX B review is required.

## While generating

1. **Describe before executing.** Before running a command that changes state (installs, migrations, deletes, network calls), say what it does and why. No silent side effects.
2. **Match the repo's conventions.** Read the surrounding code first; match its naming, structure, comment density, and idiom. New code should read like the code already there.
3. **Lean by default.** Solve the problem at hand — no speculative abstraction, no framework where a function will do. Over-engineering for the problem size is a ruler failure (CODEX A, item 2).
4. **Schema / contract discipline.** When components exchange data, define the contract explicitly and keep it consistent across producer and consumer. Contract drift is a ruler failure (CODEX A, item 3).
5. **Work on a branch or worktree.** The critic reviews the diff, so the change must be a reviewable set of uncommitted (or branch) changes in a **git repo**. `build-feature` needs git — if the target isn't a repo, stop and offer `git init`.
6. **Tests/evals are part of "done."** New behaviour gets new test/eval cases, including failure paths. The objective gate (Step 6C half 1) runs these *before* the critic review. **No tests / can't run them → fail-closed escalation**, never a silent skip.

## Security surface (decides whether CODEX B runs)

A change has a **security surface** if it touches any of: external/untrusted data, API calls, tool use, user-facing output, or data storage. When it does, run a **separate, independent** CODEX B security review (Step 6C, half 3) — never show the security reviewer the code-review findings.

Narrate security-relevant decisions as you make them: where untrusted content is delimited before it reaches a model, what privileges a component holds, what could leak and to whom, where secrets live, and where the code fails closed. The hard pass/fail lines: no auto-posting/acting without a human gate · no secrets in the codebase · fails closed on error.
