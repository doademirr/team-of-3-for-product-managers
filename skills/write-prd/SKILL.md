---
name: write-prd
description: Interview-first PRD writer. Given a rough idea, asks clarifying questions section-by-section (and absorbs unstructured brain-dumps), then drafts a grounded Product Requirements Document — never inventing requirements. Use when you need to write or refine a PRD.
---

Interview-first PRD assistant. The user gives a rough idea; this skill interviews them to gather the real inputs, then drafts a grounded PRD. The section-by-section questions double as a lesson in PRD anatomy — useful for anyone newer to PRDs. **Never invent requirements or evidence:** gaps become open questions or flagged assumptions, never fabricated prose.

## Step 1: Read reference files

Read before interviewing, so the questions and draft are grounded in how product is built at a small (20–50 person) scale-up:
1. `PLAYBOOK.md` — the *definition* phase (what a PRD must contain).
2. *(Optional — regulated domains only)* a HealthTech/AI or regulatory checklist of your own, **if** the feature involves AI or is a regulated medical device (e.g. SaMD class, AI-specific metrics, regulatory sections). Ground the AI/regulatory sections against it.

## Step 2: Get the seed

Ask the user for a rough one-liner if they haven't given one — no polish needed. Confirm the job-to-be-done in one sentence and **reflect it back** before going further.

## Step 3: Interview — section by section, but absorb brain-dumps

Default rhythm: walk the sections below in order, asking each group's questions. Briefly say what each section is *for* as you reach it (the teaching layer).

**Many people think by writing, often in unstructured waves.** When the user brain-dumps:
- Parse the dump; map each fragment to the right PRD section.
- Tell them **what you captured and where you slotted it**.
- Then ask **only about the genuine gaps** that remain.
- Never march them back through questions they have already answered in the dump.

Interview rules:
- Only ask a question if its answer would change the PRD. A short, high-value pass — not an interrogation.
- "I don't know yet" is valid → record it as an open question and move on.
- Reflect the problem back to confirm shared understanding **before** moving to the solution.
- Flag risky assumptions as you hear them.

### Question bank (by section)
- **Problem & user** — Who is this for (primary vs secondary)? What pain, and what evidence backs it? Why now? How do they solve it today?
- **Success** — What does success look like? How do we measure it (quantified)? What is explicitly *out of scope*?
- **Solution shape** — How should users interact with it (key behaviours — the *what*, not the *how*)? Minimum viable scope? Which assumptions are risky?
- **Technical & compliance** — Platform(s)? Systems to integrate with or protect? Performance needs? Compliance (HIPAA/GDPR/accessibility)?
- **AI-specific (only if applicable)** — Accuracy target? Acceptable failure/hallucination bounds? Where is the human-in-the-loop gate? Which AI-specific metrics?
- **Sequencing** — Timeline/phases/milestones? Hard deadlines? Rollback plan if it's wrong?

## Step 4: Draft

Write the PRD in this structure, grounded **only** in the user's answers:
1. Problem & opportunity (with the evidence given)
2. Target user & JTBD
3. Goals & success metrics (quantified & testable)
4. Scope — in / out (explicit non-goals)
5. Requirements — functional + non-functional (testable, unambiguous)
6. UX / key behaviours (the *what*, not the *how*)
7. *[AI / regulated only: accuracy target, failure bounds, HITL placement, regulatory classification]*
8. Risks, assumptions, dependencies
9. Unknowns and open questions — a table: Unknown | Raised by (user / Claude / critic) | Confidence | How we'll find out | Blocks build? Include every "I don't know yet", low-confidence items and anything not yet concrete. Claude adds its own while drafting; the critic adds more in review. Discovery and the poke-first step set out to answer these.
10. Appendix (evidence, links)

Grounding rules:
- Never invent a requirement, metric, or piece of evidence. If it wasn't provided, it is an open question or a **flagged assumption** — say so plainly.
- Problem before solution; don't conflate them.
- Every metric quantified and testable, or flagged "needs a number."
- Mark the draft **"~70–80% — for review,"** never "final."

## Step 5: Challenge — only when it adds signal

Run one check pass and flag **only real issues**: problem/solution conflation, vague/untestable metrics, unstated scope, ungrounded claims, unaddressed risky assumptions. If a section holds, say so and move on. **Do not manufacture objections or challenge for the sake of it.**

## Step 6: Iterate

Refine with the user's input until they're satisfied. Keep it grounded; keep the gaps honest.
