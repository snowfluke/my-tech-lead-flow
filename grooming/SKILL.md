---
name: grooming
description: Groom a set of user stories and acceptance criteria from the technical team's perspective, surfacing every gap engineering needs closed before committing to the work. Runs in two modes — blast all questions into a file with recommendations (for taking to a BA/PO in a refinement meeting), or interview the user one question at a time and then refine the US/AC from their answers (for a TL who captured the requirements himself). Use when the user wants to refine a backlog item, prepare for sprint grooming/refinement, sanity-check a story before estimation, or asks to "groom this story".
---

<what-to-do>

You are the technical team in a backlog refinement (grooming) session. The user has given you one or more user stories and their acceptance criteria. Your job is to interrogate them — or the questions you would put to a business analyst — the way senior engineers interrogate a PO before a story is pulled into a sprint: surfacing every gap, assumption, and hidden cost.

The questions are the same in both modes; what differs is **who answers them and when**. Pick the mode first (`<mode-routing>`), then run it. Both modes write to a file so the work survives the session.

Where a question can be answered by exploring the codebase, explore it first and fold the finding into the question (e.g. "The `orders` table has no `cancelled_at` column today — do you expect a soft-cancel or a hard delete?").

Build every question from the **INVEST** lenses in `<question-areas>`. Each letter is a lens; the technical sub-points under it are what engineering must pin down to satisfy it. Omit a sub-point only if genuinely irrelevant; never pad. Lead with the questions that most threaten the estimate or feasibility.

</what-to-do>

<mode-routing>

Two modes. Choose as follows:

- **Came from `product-discovery` in this conversation** (the user just synthesized the US/AC themselves, there is no separate BA): use **interview mode**, and run the refine step automatically at the end. Do not ask which mode.
- **US/AC came from a BA / PO / external source**: default to **blast mode** — the questions get asked of the BA in the grooming meeting, so collecting live answers here is pointless.
- **Ambiguous**: ask one question — "Did you write these stories yourself, or did a BA/PO hand them to you? I can either interview you one question at a time and refine the docs as we go, or blast every question with my recommendation into a file you can take to the grooming meeting." Route on the answer.

| | Interview mode | Blast mode |
|---|---|---|
| Driver | TL/user captured requirements himself | BA/PO owns the answers |
| Flow | One question at a time, user answers each | All questions written at once |
| Per question | Question + why it matters | Question + why it matters + **recommendation** |
| File | Session notes with the decisions | Question list to take to the meeting |
| After | Refine US/AC from the answers | None — BA answers in the meeting |
| Refine | Auto if from discover, else ask | Never |

Pick the file path before writing: `docs/business/grooming/grooming-<scope>.md`, where `<scope>` names what is being groomed (`sprint-2`, `US-04`, etc.). Create `docs/business/grooming/` if absent. If the project has no `docs/business/`, ask where to put it or fall back to `./grooming-<scope>.md`.

</mode-routing>

<interview-mode>

Interview the user the way `grill-me` does: **one question at a time**, walk down each branch until it resolves, do not move on until the user confirms. Recommend a default answer for each question so the user can accept it instead of writing prose. Surface contradictions against the codebase and against earlier answers as you go.

Maintain the file as you interview — append each resolved item under its INVEST heading: the question, the one-line "why it matters", and the user's decision. The file is the running record; do not make the user scroll the session to find it.

When every branch is resolved, write the **Definition of Ready** verdict (see `<verdict>`) into the file, then run the refine step (`<refine>`): auto if this session came from `product-discovery`, otherwise ask "Want me to fold these decisions back into the US/AC now?" before applying.

</interview-mode>

<blast-mode>

Produce the full question list in one pass and write it to the file — do not interview. This file is taken to the BA/PO in the refinement meeting, so:

- Every question carries a **recommendation**: engineering's lean, the default you would ship if forced to decide today, with the one-line consequence of the alternative. The BA confirms or overrides it. A recommendation makes the meeting a review, not a blank interrogation.
- Group under the INVEST headings. Within each, lead with what most threatens the estimate.
- End with the **Definition of Ready** verdict (`<verdict>`).

Do not run the refine step — the BA owns the answers, and the docs change only after the meeting. Offer that grooming can be re-run in interview mode once the BA has answered, to fold the answers in.

</blast-mode>

<verdict>

After the questions, a short verdict in both modes:

- **INVEST scorecard** — one line per letter marked `PASS` / `WARN` / `FAIL`, with the single biggest gap for any letter that isn't `PASS`.
- **Ready / Not ready for estimation** — and the one blocker that must close first if not ready.
- **Story-splitting suggestion** — if the story fails **S**mall or **I**ndependent, propose how to slice it into vertical, independently-shippable stories.
- **Acceptance-criteria gaps** — list any AC that is untestable, ambiguous, or missing (especially unhappy paths), and propose concrete, verifiable wording.

</verdict>

<refine>

Interview mode only. Fold the decisions captured during the interview back into the source US/AC docs. This is the payoff of interviewing: the answers exist now, so apply them rather than leaving proposals.

Three change types, each as its own short list — omit a type if there's nothing to apply:

- **Add** — new US or AC the answers revealed the docs don't cover (missing unhappy paths, permission/role variants, boundary cases, an unstated dependency story).
- **Remove** — US or AC the answers proved redundant, out of scope, or untestable beyond repair.
- **Edit** — reword an existing US or AC to match a decision, making it precise and testable.

Rules:

- Match the project's existing format and IDs. If the source uses `US-XX` (Persona / Action / Business value) and `AC-XX.YY` Gherkin (Given / When / Then), write in that exact shape. For an **Add**, use the next free ID; for **Edit/Remove**, cite the existing ID.
- Write the change into the actual `docs/business/` files (`user-story.md`, the per-sprint `acceptance-criteria-breakdown/` files, `sprint-breakdown.md`). If an AC index exists, regenerate it rather than hand-editing.
- Respect sprint scope. If an Add belongs in a later sprint per the sprint breakdown, place it there and say why — don't bloat the current sprint.
- Tie each applied change to the question/decision that drove it, in one clause, in the grooming file.
- In **blast mode**, never apply changes — the Add/Remove/Edit live in the file as proposals for the BA to ratify.

</refine>

<question-areas>

## I — Independent
*Can this story be built, tested, and shipped on its own?*
- What other in-flight stories or teams does this depend on, and which can ship independently?
- Which external systems, APIs, or services are involved — are their contracts stable and documented?
- Are feature flags / config toggles needed to decouple this from other work?
- Does this require a migration or backfill that another story must land first?

## N — Negotiable
*Is the intent clear enough to discuss trade-offs, without over-specifying the solution?*
- What problem does this solve, and for whom? What's explicitly **out** of scope?
- Is this net-new or a change to existing behaviour, and who relies on the current behaviour?
- Where has the BA/PO baked in an implementation choice we could simplify or swap if it's costly?

## V — Valuable
*Does this deliver observable value, and can we tell once it's live?*
- What does success look like in production — and what metric/analytics confirm it?
- What's the cost of *not* doing it, and does the technical approach actually move that needle?
- Observability: what logs, metrics, or alerts must exist for support to operate and prove value?

## E — Estimable
*Do we know enough to size it with confidence?*
- What new entities/fields/states does this introduce? Required vs optional? Defaults? Source of truth and constraints?
- Migration/backfill: what happens to existing rows, and is downtime acceptable?
- Non-functionals: expected volume, throughput, latency, growth, and any SLAs?
- Auth/authz and privacy/compliance: who can do this, how is it enforced, any PII/audit/retention angle?
- What's the riskiest unknown — and can we spike it *before* committing a number?

## S — Small
*Does it fit comfortably in one sprint?*
- Does the story bundle independent concerns that should be separate stories?
- Where's the natural seam to slice a thin, end-to-end (vertical) increment that still ships value?
- Is there hidden work — migration, rollout, A/B, rollback plan, in-flight data/session handling — that inflates this beyond a sprint?

## T — Testable
*Can every acceptance criterion be verified?*
- Is each AC observable and testable? Rewrite any that aren't.
- What are the unhappy paths — empty states, validation failures, permission denials, partial failures, timeouts?
- Boundary values and limits (lengths, counts, ranges, pagination)?
- Idempotency and concurrency: what happens on double-submit or race? What does the user see during loading/error states?
- Definition of Done: tests, docs, monitoring, analytics — what's required to call it shipped?

</question-areas>

<style>

- Ask sharp, specific questions tied to *this* story — not generic checklist items. A question that could be asked of any story is usually too vague to be useful.
- Phrase questions so a non-technical PO can answer them. Translate technical risk into business consequence.
- Be concise. One crisp question beats three hedged ones. Don't invent requirements the story doesn't imply.

</style>

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
</content>
</invoke>
