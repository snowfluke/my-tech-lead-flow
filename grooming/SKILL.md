---
name: grooming
description: 'Groom a set of user stories and acceptance criteria from the technical team''s perspective, surfacing every gap engineering needs closed before committing to the work. Runs in two modes: blast all questions into a file with recommendations (for taking to a BA/PO in a refinement meeting), or interview the user one question at a time and then refine the US/AC from their answers (for a TL who captured the requirements himself). Use when the user wants to refine a backlog item, prepare for sprint grooming/refinement, sanity-check a story before estimation, or asks to "groom this story".'
---

<what-to-do>

You are the technical team in a backlog refinement (grooming) session. The user has given you one or more user stories and their acceptance criteria. Your job is to interrogate them (or the questions you would put to a business analyst) the way senior engineers interrogate a PO before a story is pulled into a sprint: surfacing every gap, assumption, and hidden cost.

The questions are the same in both modes; what differs is **who answers them and when**. Pick the mode first (`<mode-routing>`), then run it. Both modes write to a file so the work survives the session.

Where a question can be answered by exploring the codebase, explore it first and fold the finding into the question (e.g. "The `orders` table has no `cancelled_at` column today: do you expect a soft-cancel or a hard delete?").

Build every question from the **INVEST** lenses in [references/question-areas.md](references/question-areas.md). Each letter is a lens; the technical sub-points under it are what engineering must pin down to satisfy it. Omit a sub-point only if genuinely irrelevant; never pad. Lead with the questions that most threaten the estimate or feasibility.

</what-to-do>

<mode-routing>

Two modes. Choose as follows:

- **Came from `product-discovery` in this conversation** (the user just synthesized the US/AC themselves, there is no separate BA): use **interview mode**, and run the refine step automatically at the end. Do not ask which mode.
- **US/AC came from a BA / PO / external source**: default to **blast mode**, because the questions get asked of the BA in the grooming meeting, so collecting live answers here is pointless.
- **Ambiguous**: ask this one question. "Did you write these stories yourself, or did a BA/PO hand them to you? I can either interview you one question at a time and refine the docs as we go, or blast every question with my recommendation into a file you can take to the grooming meeting." Route on the answer.

| | Interview mode | Blast mode |
|---|---|---|
| Driver | TL/user captured requirements himself | BA/PO owns the answers |
| Flow | One question at a time, user answers each | All questions written at once |
| Per question | Question + why it matters | Question + why it matters + **recommendation** |
| File | Session notes with the decisions | Question list to take to the meeting |
| After | Refine US/AC from the answers | None: BA answers in the meeting |
| Refine | Auto if from `product-discovery`, else ask | Never |

Pick the file path before writing: `docs/decisions/<YYYY-MM-DD>-grooming-<scope>.md`, where `<scope>` names what is being groomed (`sprint-2`, `US-04`, etc.). Create `docs/decisions/` if absent. Grooming files sit with the other decision logs.

</mode-routing>

<interview-mode>

If a blast-mode file for this scope already holds the BA's answers, read it first. Apply each answered question as a decision, and interview only about the questions still open.

Interview the user the way `grill-me` does: **one question at a time**, walk down each branch until it resolves, do not move on until the user confirms. Recommend a default answer for each question so the user can accept it instead of writing prose. Surface contradictions against the codebase and against earlier answers as you go.

Maintain the file as you interview: append each resolved item under its INVEST heading: the question, the one-line "why it matters", and the user's decision. The file is the running record; do not make the user scroll the session to find it.

When every branch is resolved, write the **Definition of Ready** verdict (see `<verdict>`) into the file, then run the refine step (`<refine>`): auto if this session came from `product-discovery`, otherwise ask "Want me to fold these decisions back into the US/AC now?" before applying.

</interview-mode>

<blast-mode>

Produce the full question list in one pass and write it to the file; do not interview. This file is taken to the BA/PO in the refinement meeting, so:

- Every question carries a **recommendation**: engineering's lean, the default you would ship if forced to decide today, with the one-line consequence of the alternative. The BA confirms or overrides it. A recommendation makes the meeting a review, not a blank interrogation.
- Group under the INVEST headings. Within each, lead with what most threatens the estimate.
- End with the **Definition of Ready** verdict (`<verdict>`).

Do not run the refine step: the BA owns the answers, and the docs change only after the meeting. Once the BA has answered in the file, re-run grooming in interview mode on it: it applies the answers and asks only what is still open.

</blast-mode>

<verdict>

After the questions, a short verdict in both modes:

- **INVEST scorecard**: one line per letter marked `PASS` / `WARN` / `FAIL`, with the single biggest gap for any letter that isn't `PASS`.
- **Ready / Not ready for estimation**: and the one blocker that must close first if not ready.
- **Story-splitting suggestion**: if the story fails **S**mall or **I**ndependent, propose how to slice it into vertical, independently-shippable stories.
- **Acceptance-criteria gaps**: list any AC that is untestable, ambiguous, or missing (especially unhappy paths), and propose concrete, verifiable wording.

</verdict>

<refine>

Interview mode only. Fold the decisions captured during the interview back into the source US/AC docs. This is the payoff of interviewing: the answers exist now, so apply them rather than leaving proposals.

Three change types, each as its own short list; omit a type if there's nothing to apply:

- **Add**: new US or AC the answers revealed the docs don't cover (missing unhappy paths, permission/role variants, boundary cases, an unstated dependency story).
- **Remove**: US or AC the answers proved redundant, out of scope, or untestable beyond repair.
- **Edit**: reword an existing US or AC to match a decision, making it precise and testable.

Rules:

- Match the project's existing format and IDs. If the source uses `US-XX` (Persona / Action / Business value) and `AC-XX.YY` Gherkin (Given / When / Then), write in that exact shape. For an **Add**, use the next free ID; for **Edit/Remove**, cite the existing ID.
- Write the change into the actual `docs/business/` files (`user-story.md`, the per-sprint `acceptance-criteria-breakdown/` files, `sprint-breakdown.md`). Then regenerate the AC index: `python3 <us-ac-formatter dir>/scripts/build_ac_index.py --business-dir docs/business --write`.
- If `docs/business/` does not exist yet (grooming right after `product-discovery`), apply the changes to the requirements table instead, and hand the refined table to `us-ac-formatter`, which writes the files.
- Respect sprint scope. If an Add belongs in a later sprint per the sprint breakdown, place it there and say why; don't bloat the current sprint.
- Tie each applied change to the question/decision that drove it, in one clause, in the grooming file.
- In **blast mode**, never apply changes: the Add/Remove/Edit live in the file as proposals for the BA to ratify.

</refine>

<style>

- Ask sharp, specific questions tied to *this* story, not generic checklist items. A question that could be asked of any story is usually too vague to be useful.
- Phrase questions so a non-technical PO can answer them. Translate technical risk into business consequence.
- Be concise. One crisp question beats three hedged ones. Don't invent requirements the story doesn't imply.

</style>

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
