---
name: write-user-stories
description: Turns a PRD or feature description into well-formed user stories with acceptance criteria. Detects the level first (epic / story / task / spike) and applies the right template for each, checks every story against INVEST, and never invents requirements. Use when you need to break a PRD or feature into stories.
---

Turns a PRD (best case) or a raw feature description into a set of well-formed user stories with acceptance criteria. Interview-*light* — a good PRD already holds most inputs — with a teaching layer for anyone newer to the craft. Picks up exactly where `write-prd` stops (that skill ends at the PRD; this one breaks it into stories). **Convergent:** a story either meets the quality bar or it doesn't. **Never invent requirements or acceptance criteria** — gaps become open questions, never fabricated prose.

## The craft this skill applies (canonical, stable — no web research needed)

- **Connextra template** — "As a [user], I want [goal], so that [benefit]." The *benefit* clause is non-negotiable; a story without it is a task.
- **INVEST** (Bill Wake) — the quality bar every story is checked against: **I**ndependent, **N**egotiable, **V**aluable, **E**stimable, **S**mall, **T**estable.
- **Acceptance criteria — two styles**, chosen per story: **Given/When/Then** (Gherkin — for scenario/behaviour) · **rule/checklist** (for a list of conditions). Don't force G/W/T onto everything.
- **Vertical slice + SPIDR splitting** (Mike Cohn) — a story is a thin end-to-end slice, not a horizontal layer. Split too-big stories along **S**pikes, **P**aths, **I**nterfaces, **D**ata, **R**ules.
- **Hierarchy** — epic → story → task, plus **spike** as a special case. Cap it there; do not drag in themes/initiatives (enterprise-portfolio machinery, out of scope for a small scale-up).

## Step 1: Get the input

Detect or ask which:
- **A PRD** (best case) — read it; it already holds users, JTBD, scope, requirements, success metrics. If it came from `write-prd`, even better.
- **A raw feature description** — a rougher seed. Fine; you'll gather more in Step 2.

**Many people think by writing, often in unstructured waves.** When the user brain-dumps, parse it, map each fragment to the right place, tell them what you captured and where, then ask only about genuine gaps. Never march them back through what they've already answered.

## Step 2: Map users + epics

- Identify the **personas** this feature serves (primary vs secondary).
- Identify the **epic(s)** — the big body of work this breaks into.
- **Reflect the breakdown back** and confirm before splitting into stories.

## Step 3: Draft the story list

List the stories grouped by **user journey / epic**, in **priority order**. Aim for thin vertical slices. Say briefly what each grouping is *for* (teaching layer).

## Step 3.5: Detect the level first — then apply that level's template

For **each item**, decide its level *before* writing it, and use the matching template. The level drives the shape — there is no one-size template.

| Level | Template | Acceptance | Owner |
|---|---|---|---|
| **Epic** | A container, not a slice. **Title + outcome + success measure + list of child stories.** May use "As a [user]…" but broad. **No G/W/T.** | A metric moves | PM |
| **Story** | **Connextra + INVEST + acceptance criteria** (G/W/T *or* rules). Thin vertical slice, fits a sprint. The main artifact. | Testable AC per story | PM |
| **Task** | **Not** user-voice — imperative, for the engineer ("Add index to X table"). No user, no benefit. | Binary: done / not done | Usually **eng**, not PM |
| **Spike** | A **time-boxed investigation**, not shippable output ("Investigate whether X is feasible"). | Deliverable = a decision/answer | PM or eng |

**Flag level mismatches** (this is the backbone of the challenge pass):
- A "story" that's really an **epic** → too big; propose a SPIDR split into child stories.
- A "story" that's really a **task** → no user or benefit; name it as an implementation detail eng owns, don't dress it as a story.
- For **tasks**: *recognise* them and say "this is a task — eng writes these." Don't over-generate implementation steps that aren't the PM's job.

## Step 4: Write each item

- **Stories:** Connextra form + acceptance criteria (G/W/T or rules, whichever fits). As you write, **name the INVEST criterion each choice satisfies** (the teaching layer) — e.g. "splitting here keeps it **S**mall and **E**stimable."
- **Epics:** outcome + success measure + child-story list.
- **Spikes:** the question, the time-box, the deliverable.
- **Non-functional needs** (performance, security, accessibility, compliance) — surface as constraints on the relevant stories or as dedicated NFR stories. Never silently drop them.

## Step 5: Challenge — only when it adds signal

One check pass, flag **only real issues**: task-masquerading-as-story (missing user/benefit), untestable acceptance criteria, an oversized story that needs splitting, a wrong-level item, or an **invented** requirement. If a story holds, say so and move on. **Do not manufacture objections.**

## Step 6: Iterate

Refine with the user's input until they're satisfied.

## Grounding rules (same discipline as `write-prd`)

- **Never invent a requirement or acceptance criterion.** If the PRD doesn't say it, it's an **open question**, not fabricated AC.
- Mark the output **"~70–80% — for review,"** never "final."
- Problem/user before solution; the benefit clause must be real, not reverse-engineered to fit.
