# Team of 3

A multi-agent critic loop for product and coding work, built as a set of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills.

Three roles, deliberately asymmetric:

- **You** — the human PM and decision-maker.
- **Claude** — the *generator and owner*. Drafts the artifact (a PRD, user stories, a decision frame, or code), holds it, and runs the loop.
- **An independent critic model** — the *honest critic*. This build uses OpenAI's [Codex CLI](https://github.com/openai/codex). It has no relationship to the author and no incentive to soften; its only job is to find real gaps against a fixed ruler.

Claude and the critic iterate directly. **You only see output when an escalation rule fires** — a finished artifact, a question only you can answer, or an honest "the critic was unavailable, so this was not independently reviewed." The rest of the loop runs quietly.

## Why it's built this way

- **Asymmetric roles beat a panel of clones.** A generator that also grades itself is a sycophancy machine. Separating "owns the work" from "critiques the work" — and giving the critic no stake in the outcome — is what makes the review honest.
- **Fixed rulers, not vibes.** Each task is judged against a specific checklist (definition-of-done for convergent tasks; a decision-frame check for the divergent one), so the critique is measurable and repeatable rather than a matter of taste.
- **Fail closed.** Any seam failure — timeout, empty response, malformed output — returns `UNABLE_TO_REVIEW`, and the artifact is surfaced labelled *not independently reviewed*. Silence is never treated as approval.
- **A committed eval gate.** The critic seam has its own test suite (`test-critic.sh`) that dogfoods the harness's own coding ruler.
- **Convergent *and* divergent.** Most tasks converge on one right answer (a PRD either meets the bar or it doesn't). Prioritisation doesn't — so its critic judges the *decision frame*, never the choice, and always hands the call back to you.

## What's inside

```
skills/
├── team-of-3/          the harness: the loop, the rulers, the critic seam
│   ├── SKILL.md            the orchestration
│   ├── critic.sh           the single model-invocation seam (swap this to swap critics)
│   ├── verdict.schema.json the structured verdict contract
│   ├── test-critic.sh      the committed eval gate for the seam
│   └── projects/           cross-session project memory (one file per project)
├── write-prd/          generator: interview-first PRD writer
├── write-user-stories/ generator: PRD → INVEST-checked user stories
└── prioritise-ideas/   generator: divergent decision framing
PLAYBOOK.md             the 0→1 product playbook the generators ground on
CODING-PRACTICES.md     the baseline the build-feature task follows
```

The wired tasks: **write-prd**, **write-user-stories**, **prioritise-ideas** (divergent), and **build-feature** (code). One shared loop; only the generator and ruler change per task.

## Requirements

- **[Claude Code](https://docs.claude.com/en/docs/claude-code)** — the skills run inside it.
- **[Codex CLI](https://github.com/openai/codex)** — the critic. Authenticated via its own ChatGPT session (`codex` handles this; **no API key is stored in this repo**). Built and verified against `codex-cli` 0.143.0; pin your own version and re-run `test-critic.sh` after upgrades.
- **Python 3** and **bash** — used by the seam for canonicalisation and the portable timeout.

## Install

1. Copy the `skills/` folders into your project's `.claude/skills/` (or your user-level skills directory).
2. Copy `PLAYBOOK.md` and `CODING-PRACTICES.md` where the skills expect them (repo root, or adjust the paths in the SKILL files).
3. Make the seam executable: `chmod +x .claude/skills/team-of-3/*.sh`
4. Verify the seam: `bash .claude/skills/team-of-3/test-critic.sh` → `ALL GREEN`.
5. In Claude Code, run `/team-of-3` and name your task (or let it locate your stage in the 0→1 build).

## The playbook

The generators ground on `PLAYBOOK.md` — a 0→1 product-launch playbook for HealthTech. It's the public companion to the full write-up:
**["0→1 Product Launch Playbook in HealthTech"](https://www.doafitzgerald.com/p/01-product-launch-playbook-in-healthtech)**.

## Author

Built by **Doa Fitzgerald** — Product Manager, writing on product, AI, and HealthTech at [doafitzgerald.com](https://www.doafitzgerald.com). Licensed under MIT (see `LICENSE`).
