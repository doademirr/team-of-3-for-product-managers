# Gatekeeper

The Gatekeeper decides who decides: Claude alone, or the PM (in `/team-of-3`, the user). Before Claude acts on a decision the PM hasn't made, it sorts it with the questions below and brings the PM anything the rules don't settle. It never invents a rule.

**How it's used:** `/team-of-3` Step 4.5 runs it for every project. It starts in **advice mode**: it can send the PM a decision that the project's own rules would let Claude make, but never the other way, and solo calls stay off until the Advice log meets the bar in Step 4.5.

**What's shared and what's per project:** the questions, the Always-Red list and the PM's defaults are the same for every project. Each project's file holds three inputs on a **Gatekeeper** line: its harm question (Q1), its own Red list (Q2) and its tenets (Q3). A project without them is skipped in advice mode; once solo calls are on, it sends everything to the PM.

## The questions, in order

Stop at the first question that gives an answer.

| # | Question | If yes | Why this order |
|---|---|---|---|
| 1 | Does it touch the project's harm question, however rare? | **PM** | Severity comes first. "Rare" doesn't remove a hazard. |
| 2 | Is anything Red? Always Red: anything public, data loss, tangled to undo, over 1 hour of agent work, changes the data model, changes how results are calculated (including filling an unknown value with an estimate), changes what's in or out of a release, a claim to users about their health or safety. Plus the project's own Red list. | **PM** | Red waits for the PM, whoever raised it. A tenet can't make a Red item Green. |
| 3 | Does a tenet or recorded decision already answer it? | **Apply it, log it** | A rule agreed in advance saves asking twice. |
| 4 | Does it break the main result for normal use, or could it make a result slightly wrong? If how often it happens is unknown, measure it first if that takes under 15 minutes. | Breaks it: **Fix it,** and give the numbers. Slightly wrong: carry on to 5. Unknown and can't be measured: **PM**. | Core gaps get fixed. A slightly wrong result is a quality question, not a harm question. A fix needs numbers, so how often is measured, not assumed. |
| 5 | Would fixing it change any result users see, or any decision we'd make? | If no: **Log, don't build** | Work that changes nothing isn't worth doing. |
| 6 | Is it reversible in minutes and cheap? | **Default, log it** | Two-way doors go fast. |
| 7 | Anything left | **PM** | When unsure, the Gatekeeper asks. |

## The outcomes

| Outcome | Meaning |
|---|---|
| **PM** | Stop and wait. State the question, the options and a recommendation. To get the recommendation, carry on through Q3 to Q6 as if Q1 and Q2 hadn't fired: a rare case that doesn't break the main result is recommended for logging. Base it on the project's tenets, then the PM's defaults. For a change to how results are calculated, give the options and their trade-offs, with no recommendation. |
| **Apply it, log it** | Apply the tenet or recorded decision that answers it, name it, and log it. |
| **Fix it** | Build it. Give the numbers showing what it breaks. |
| **Default, log it** | Pick the safe option, keep going, and flag it for the PM to confirm if the project's own rules ask for that. |
| **Log, don't build** | Record it where the project logs known limits, with what was accepted. |

## Rules for the Gatekeeper

- **Frequency can't decide alone.** Harm is checked first, however often it happens. For a quality gap, how often it happens is measured, not assumed.
- **Nothing disappears.** Everything not built is logged.
- **A rule can't settle a problem it causes.** If a finding is a side effect of a tenet or decision, that tenet doesn't answer it. Treat the finding as new.
- **Data loss means users' own data can't be got back.** A crash or a report that can simply be run again isn't data loss.
- **Critic disagreements go by severity.** After 3 rounds, moderate and critical issues go to the PM, and minor ones are logged.
- **Tiebreakers apply only when both options are acceptable.** Red always comes first.
- **Each answer names its question number and the rule used,** so the PM can check the reasoning.

## The PM's defaults (every project)

How the PM decides when a project's tenets are silent. They shape the recommendation only and never settle a decision on their own. These are the author's; replace them with your own.

1. A small, labelled estimate beats no answer, as long as a wrong guess can't change the result. If it could, ask, or leave it unknown and say so.
2. Ship the useful version, then make it more accurate over time.
3. Don't give users work that doesn't improve their result.

## Advice log

Step 4.5 adds a row for every decision that reaches the PM, whichever rule sent it. "Needed the PM?" is the PM's answer. The log holds real product decisions, so keep it private if they are.

| Date | Project | Finding or proposal | Gatekeeper's sort and recommendation | PM's call | Needed the PM? | Recommendation matched? |
|---|---|---|---|---|---|---|
