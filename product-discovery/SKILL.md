---
name: product-discovery
description: Optional pre-pipeline skill for when there are no user stories or acceptance criteria yet. Interviews the user about a raw product idea, then synthesizes the result into the Markdown table of user stories, acceptance criteria, and a sprint breakdown that the rest of the tech-lead pipeline (grooming, us-ac-formatter) consumes as its step-1 input. Use when the user has an idea but no written requirements, wants to start a project from scratch, says "I don't have user stories yet", "help me figure out the requirements", "turn this idea into stories", or asks where to begin.
---

# Product Discovery

The entry ramp to the pipeline for anyone starting from an idea rather than a written spec. The pipeline's first input is a Markdown table of user stories, acceptance criteria, and a sprint breakdown; this skill produces that table by interviewing the user and synthesizing their answers. It is optional: skip it if the user already has stories and AC.

Two phases: **interview to elicit the product, then synthesize the requirements table.**

## Phase 1 — Interview

Elicit the product the way `grill-me` interviews a plan: one question at a time, recommend an answer for each, walk down each branch until it resolves, and do not move on until the user confirms. The goal is to extract enough to write real stories, not to design the solution. Cover, adapting to the idea:

- **Problem and outcome.** What problem does this solve, for whom, and what does success look like? What happens today without it?
- **Users and roles.** Who uses it? Name the distinct personas/roles and what separates them (permissions, goals). Roles drive both stories and later RBAC.
- **Core jobs.** For each persona, the concrete jobs they need to do, start to finish. These become user stories. Push for the real workflow, including the unhappy paths.
- **Key entities and lifecycle.** The main things the system tracks and the states they move through. A state machine here becomes acceptance criteria later.
- **Scope.** What is explicitly in for the first release and what is deferred. Pin a Phase 1 boundary so the stories do not sprawl.
- **Constraints.** Hard requirements: integrations, compliance, volume, languages/locales, deadlines.

Surface contradictions and gaps as you go. When the picture is complete, summarize it back and confirm before writing.

## Phase 2 — Synthesize the requirements table

Turn the interview into a draft the pipeline can consume. Produce three things as Markdown, in this shape:

**User stories** — one row per story:

```
| ID | Persona | Action | Business value |
| --- | --- | --- | --- |
| US-01 | <role> | <what they do> | <why it matters> |
```

**Acceptance criteria** — one row per criterion, tied to its story (scenario-level is enough at this stage; the pipeline refines the full Given/When/Then later):

```
| AC ID | US | Scenario | Expected outcome |
| --- | --- | --- | --- |
| AC-01.01 | US-01 | <short scenario name> | <observable result> |
```

**Sprint breakdown** — a proposed grouping of stories into sprints with a one-line goal each. Sequence so foundational stories (auth, core entity creation) land first and dependent stories follow.

Rules for the synthesis:

- Cover the happy path and the obvious unhappy paths (validation, permission, empty states) for each story. Thin AC now means a weak grooming pass later.
- Trace every story to a persona and a stated job from the interview. Do not invent scope the user did not describe; if something is needed but unconfirmed, list it as an open question, not a story.
- Number `US-01`, `US-02`; `AC-<story>.<seq>`. Keep IDs stable.
- Preserve the user's domain terms and any non-English labels verbatim.

## Output and handoff

Present the table for the user to review and edit directly; this is a first draft, not a final spec. Offer to save it to a scratch file (e.g. `docs/business/REQUIREMENTS-DRAFT.md`) if they want to edit in place. Do not write the final `docs/business/` files here; that is `us-ac-formatter`'s job.

When the user is happy with the draft, point them at the next step: `grooming` to stress-test it, then `us-ac-formatter` to format it into the structured `docs/business/` set. If the user works from an issue tracker instead of the file pipeline, note that `to-prd` and `to-issues` are the tracker-based alternatives.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
