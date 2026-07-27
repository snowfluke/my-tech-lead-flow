---
name: init-claude
description: Generate the project CLAUDE.md as a dense, agent-facing operating manual in the Terral/Tatanan format, at the end of the documentation pipeline just before build starts. Distills the technical specs, coding standard, task breakdown, and deployment plan into the rules an agent must hold in context: tech stack, repo layout, architecture laws (file-size cap and split strategy, layering), runtime do/don't, the verification gate, naming, type-safety, prohibitions, a context-recovery checklist, and a command quick-reference. Use when the user wants to initialize or write CLAUDE.md, an agent operating manual, AGENTS.md, or asks to "init claude".
---

# Init CLAUDE.md

Write `CLAUDE.md`: the operating manual an agent reads before touching the repo. It is not a doc like the others. The pipeline docs are the source of truth and the place to read in depth; `CLAUDE.md` is the **dense distillation** of the load-bearing rules plus pointers to those docs, written so an agent with limited context still gets the invariants right.

This runs at the **end of the documentation pipeline, just before build**: the technical specs, coding standard, task breakdown, and deployment plan already exist, and this synthesizes them. Three phases: read everything, grill the user on what the docs leave open, then write the manual. Because every agent reads this file before touching the repo, a wrong or guessed invariant here misleads every future build — so resolve the gaps before writing, never invent.

## System prompt

Append this system prompt:

```md
# Accuracy
State what you can verify. Mark everything else.
Tag load-bearing claims with confidence: high, moderate, low, unknown.
Say "I don't know" and stop. Do not fill gaps with plausible detail.
Cite sources for figures, dates, quotes, and names.
Search when a claim is current, contested, or after your cutoff.
Show the arithmetic for any number you produce.
Form your own estimate before you use mine. Compare both.

# Directness
Tell me when I am wrong. Do it in the first sentence.
Start with the answer. Skip praise and preamble.
Deliver bad news plain.
Hold your position when I push back. Change it for new evidence or a better argument.
Keep caveats that change my decision. Cut the rest.
Do not soften, hedge, or moralize unless I ask.

# Reasoning
Reason step by step on hard problems before you conclude.
State the strongest objection to your own conclusion. Then answer it.
Separate what you know from what you infer.

# Format
Match length to the question.
Write prose. Use lists for real lists.
Follow ASD-STE100: one instruction per sentence, active voice, simple tenses, 20 words maximum.
Use the /ste100 skill for manuals and specifications.

# Ambiguity
Ask one question when the request is unclear and a wrong answer is costly.
Otherwise state your assumption and proceed.
```

## 1. Read the pipeline docs

`CLAUDE.md` is a synthesis, so read its sources first and pull the real values, never invent them:

- `docs/technical-specs/` — tech stack and versions (`04`), repo layout (`03`), module/service boundaries (`05`), data model and state machines (`06`), env config (`11`).
- `CODING_STANDARD.md` — the architecture laws, naming, type-safety, error-handling, and testing rules to restate tersely.
- `docs/TASK_BREAKDOWN.md` — the work model (pre-assigned vs self-pick, scaffold model, reviewer).
- `DEPLOYMENT_PLAN.md` — environments, deploy triggers, the verification/build commands.
- `GLOSSARY.md` and `docs/business/` — domain terms, roles, language policy.
- Any existing `CLAUDE.md` to update in place rather than overwrite.

## 1b. Grill on the gaps

Don't write until the open questions are resolved. Grill the user one at a time — recommending a default and the trade-off for each — on whatever the docs leave ambiguous: the verification command set if not yet fixed, the trailer/commit policy, the file-size cap and split strategy, the layering laws, any prohibition that isn't already pinned in `CODING_STANDARD.md`. Skip what the docs already answer; never guess an invariant.

## 2. Write CLAUDE.md in the standard structure

Follow this shape (drop sections that do not apply; this is an operating manual, so it is terse, declarative, and command-dense):

1. **Title and critical header** — one line on what the project is, then a non-negotiable note: re-read this file if context was compacted, and run the verification gate before marking any task complete.
2. **Source of truth** — a pointer list mapping each concern to its authoritative doc (product to `docs/business/`, architecture to `docs/technical-specs/`, rules to `CODING_STANDARD.md`, work to `docs/TASK_BREAKDOWN.md`, ops to `DEPLOYMENT_PLAN.md`, terms to `GLOSSARY.md`). The manual restates rules tersely; the docs hold the detail.
3. **Project overview** — a tech-stack table (layer to technology) and the repository layout tree with per-folder purpose.
4. **Boundaries** — the service/module map and any roles, domains, and state machines an agent must respect.
5. **Work model** — how cards are assigned, any scaffold/contract-stable model, who reviews.
6. **Architecture laws** — the hard rules, including the **file-size cap (max 300 lines, split proactively at 250)** and the split strategy (extract into a sibling submodule folder, keep the entry point thin), the module/feature file pattern, and layering (no business logic in handlers, data access only via the repository layer, no cross-module internal imports).
7. **Runtime do/don't** — a two-column table of the tools to use and the ones banned for this stack (e.g. the package manager, test runner, and forbidden alternatives).
8. **Verification gate** — the exact ordered commands to run before any task is considered complete.
9. **Code discovery protocol** — search before writing, read similar files, reuse utilities and types.
10. **Naming** — a table of element to pattern to example.
11. **Type safety, error handling, testing, database** — the terse rules restated from the coding standard.
12. **Git** — branch and PR flow, commit format, the trailer policy.
13. **Absolute prohibitions** — a table of violation to why, the things that must never appear in merged code.
14. **Context recovery checklist** — a checkbox list of the project-specific invariants to re-verify after compaction (the easy-to-forget specifics: ID formats, role names, state-machine transitions, hashing choices, naming quirks). This is what makes the manual resilient to lost context.
15. **Quick reference** — the everyday commands (dev, build, test, db, deploy) in one fenced block.

## Writing rules

- Terse and imperative. This file is read under context pressure; every line must earn its place. Restate rules in one sentence and point to the full doc rather than copying it wholesale.
- Real values only: the actual stack versions, command names, paths, roles, and formats from the docs. No placeholders where a real value exists.
- Keep it consistent with the other docs; if `CLAUDE.md` and `CODING_STANDARD.md` disagree, the standard wins and `CLAUDE.md` must be corrected.
- Write to `CLAUDE.md` at the repo root (or `AGENTS.md` if the project uses that). Update in place if one exists; report what changed.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
