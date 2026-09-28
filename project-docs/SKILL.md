---
name: project-docs
description: Author the orientation document set that gets a newcomer (human or agent) productive (README.md, docs/GLOSSARY.md, and the docs/development-guide/ and docs/onboarding/ folders, one file per section) by reading the codebase and existing project docs, then writing what is actually true. Produces any subset the user asks for; cross-links the other docs (coding standard, task breakdown, deployment plan, and so on) instead of duplicating them. Use when the user wants a README, glossary, onboarding guide, development/getting-started guide, or "the orientation docs" for a repo.
---

# Project Docs

Author the orientation set that takes someone from "just cloned this" to "shipping a change":

| Doc | Answers | Audience |
| --- | --- | --- |
| `README.md` | What is this, why, how do I run it? | Anyone landing on the repo |
| `docs/GLOSSARY.md` | What does this *word* mean here? | Anyone reading code or specs |
| `docs/development-guide/` | How do I actually *do* a task end-to-end? | A developer picking up work |
| `docs/onboarding/` | How do I get set up and find my way around? | A brand-new contributor |

Produce whichever the user asks for; default to all four. They share one source (the codebase + existing docs) and one rule: **describe reality, then cross-link; never duplicate.** Where a fact already lives in another doc (standards, task breakdown, deployment plan, ADRs), link to it rather than restating it; restated facts drift and rot.

## 1. Read first

Before writing, build an accurate picture:

- **Run/build truth:** README, `CONTRIBUTING.md`, `CLAUDE.md`/`AGENTS.md`, manifests, lockfiles, scripts, `.env.example`, compose/Dockerfile, CI workflows. Get the *real* setup and verification commands; don't guess them.
- **Structure truth:** the directory layout, module/layer boundaries, entry points, where each responsibility lives.
- **Domain truth:** specs, user stories, ADRs, and the code itself: for the glossary, harvest the actual terms used in identifiers, UI copy, and docs (including non-English UI labels, preserved verbatim).
- **Workflow truth:** branch/PR flow, review process, sprint/task model; read `docs/task-breakdown/`, `docs/coding-standard/`, `docs/deployment-plan/` if present.

Ask the user only for what the repo can't tell you: project purpose/business context, target audience, where to get help (channels, owners), and anything intentionally undocumented. Batch these questions.

## 2. Write each requested doc

Every command must be copy-paste-runnable for this repo (real script names, paths, ports). Each folder's `_index.md` opens with a one-line project identifier and the table of contents. Follow the writing conventions below.

Write each requested doc in the layout of [references/layout.md](references/layout.md), which also says what each one holds.

## 3. Confirm and write

- For a fresh set, show the proposed outline (sections per doc) before writing, unless told to just generate.
- Write `README.md` at the repo root and the rest under `docs/`. If a doc exists, read and update it in place; preserve still-true content, refresh what drifted, report what changed. Never clobber. If a guide exists as an older single file, ask once whether to migrate it (see [references/layout.md](references/layout.md)).
- Keep the set internally consistent: the README's links, the onboarding's pointers, and the scenario guide's references should all resolve to the docs that actually exist.

## Notes

- These complement the rest of the doc pipeline (`/coding-standard`, `/task-breakdown`, `/deployment-plan`, `/troubleshooting`); generate or update those first where it makes the cross-links real.

## Helper script

For the repo-structure map in the README and the codebase walkthrough in the
onboarding guide, generate the tree rather than transcribing it by hand:

```bash
python3 <this skill's dir>/scripts/repo_tree.py . --max-depth 3
```

It prints a fenced tree skipping VCS, dependencies, build output, and caches.
Add the per-folder purpose annotations yourself; the script only guarantees the
structure is accurate.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
