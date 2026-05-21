---
name: project-docs
description: Author the orientation document set that gets a newcomer (human or agent) productive — README.md, GLOSSARY.md, DEVELOPMENT_SCENARIO_GUIDE.md, and ONBOARDING_GUIDE.md — by reading the codebase and existing project docs, then writing what is actually true. Produces any subset the user asks for; cross-links the other docs (CODING_STANDARD, TASK_BREAKDOWN, DEPLOYMENT_PLAN, etc.) instead of duplicating them. Use when the user wants a README, glossary, onboarding guide, development/getting-started guide, or "the orientation docs" for a repo.
---

# Project Docs

Author the orientation set that takes someone from "just cloned this" to "shipping a change":

| Doc | Answers | Audience |
| --- | --- | --- |
| `README.md` | What is this, why, how do I run it? | Anyone landing on the repo |
| `GLOSSARY.md` | What does this *word* mean here? | Anyone reading code or specs |
| `DEVELOPMENT_SCENARIO_GUIDE.md` | How do I actually *do* a task end-to-end? | A developer picking up work |
| `ONBOARDING_GUIDE.md` | How do I get set up and find my way around? | A brand-new contributor |

Produce whichever the user asks for; default to all four. They share one source (the codebase + existing docs) and one rule: **describe reality, then cross-link — never duplicate.** Where a fact already lives in another doc (standards, task breakdown, deployment plan, ADRs), link to it rather than restating it; restated facts drift and rot.

## 1. Read first

Before writing, build an accurate picture:

- **Run/build truth:** README, `CONTRIBUTING.md`, `CLAUDE.md`/`AGENTS.md`, manifests, lockfiles, scripts, `.env.example`, compose/Dockerfile, CI workflows. Get the *real* setup and verification commands — don't guess them.
- **Structure truth:** the directory layout, module/layer boundaries, entry points, where each responsibility lives.
- **Domain truth:** specs, user stories, ADRs, and the code itself — for the glossary, harvest the actual terms used in identifiers, UI copy, and docs (including non-English UI labels, preserved verbatim).
- **Workflow truth:** branch/PR flow, review process, sprint/task model — read `TASK_BREAKDOWN.md`, `CODING_STANDARD.md`, `DEPLOYMENT_PLAN.md` if present.

Ask the user only for what the repo can't tell you: project purpose/business context, target audience, where to get help (channels, owners), and anything intentionally undocumented. Batch these questions.

## 2. Write each requested doc

Every command must be copy-paste-runnable for this repo (real script names, paths, ports). Open each doc with a one-line project identifier and a short Table of Contents if it's long. Follow the writing conventions below.

### README.md
The front door, kept lean. What the project is and the problem it solves; key tech/stack; a quickstart (prerequisites → install → run → test) that actually works; a high-level repo-structure map; and links out to the deeper docs (onboarding, glossary, standards, deployment) rather than inlining them. Badges/license/contributing pointer if the project uses them.

### GLOSSARY.md
A pure glossary — definitions only, no implementation detail. Group terms by domain area (e.g. domain entities, lifecycle/status, actions/buttons, roles). Each entry: the canonical term, its UI label if different (quote non-English labels verbatim), and a one-to-two-sentence definition. Disambiguate overloaded words ("account = Customer, not User"). Pull terms from real usage; don't invent vocabulary the project doesn't use.

### DEVELOPMENT_SCENARIO_GUIDE.md
Concrete, role-based walkthroughs of the recurring jobs, start to finish. Typically: Day 1 setup; the work-split / sprint model; picking up and completing a task of each kind (e.g. backend card, frontend card) test-first through to commit; reviewing a PR; promoting/releasing. Each scenario is an ordered, runnable sequence of steps with the exact commands, referencing the relevant skills/docs at each step (e.g. "run the verification gate per CODING_STANDARD.md", "review per the checklist"). This is the "how we work here" doc.

### ONBOARDING_GUIDE.md
The newcomer's path, in order: project context (what/why, domain in a paragraph); prerequisites (tools + versions); local setup (automated path and manual fallback, both verified); a codebase walkthrough (the map plus what to read first); the development workflow in brief (linking the scenario guide for depth); key concepts to internalize (linking the glossary); and where to get help. Should get a new contributor to a green local build and first change.

## 3. Confirm and write

- For a fresh set, show the proposed outline (sections per doc) before writing, unless told to just generate.
- Write to where the project keeps docs (`docs/` or repo root for README). If a doc exists, read and update it in place — preserve still-true content, refresh what drifted, report what changed. Never clobber.
- Keep the set internally consistent: the README's links, the onboarding's pointers, and the scenario guide's references should all resolve to the docs that actually exist.

## Notes

- These complement the rest of the doc pipeline (`/coding-standard`, `/task-breakdown`, `/deployment-plan`, `/troubleshooting`); generate or update those first where it makes the cross-links real.
- If the user wants a shareable onboarding link for teammates, the `ShareOnboardingGuide` tool uploads an `ONBOARDING.md` and returns a link.

## Helper script

For the repo-structure map in the README and the codebase walkthrough in the
onboarding guide, generate the tree rather than transcribing it by hand:

```bash
python scripts/repo_tree.py . --max-depth 3
```

It prints a fenced tree skipping VCS, dependencies, build output, and caches.
Add the per-folder purpose annotations yourself; the script only guarantees the
structure is accurate.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
