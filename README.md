# Tech Lead Skills

Agent skills that take a product from an idea to reviewed code. Each skill reads
the documents the previous one wrote and writes the next, so the specs, the
board, and the code stay in step, and every card traces back to an acceptance
criterion.

## Install

The flow calls `grill-me` and `tdd` from
[engineering-skills](https://github.com/snowfluke/engineering-skills). Install
both repositories:

```bash
npx skills add snowfluke/tech-lead-skills -g
npx skills add snowfluke/engineering-skills -g
```

The `skills` CLI installs into any agent it supports (Claude Code, opencode,
Codex, and others). Add `-s <name>` to install one skill.

To edit and publish the skills, clone this repository and run `./link.sh`. It
links every skill into `~/.claude/skills` (or the directory you pass), so edits
land in the clone.

## Where to start

| Situation | Start with |
| --- | --- |
| An idea, no user stories yet | `product-discovery` |
| User stories exist, new project | `grooming` |
| A running project without these docs | `adopt-flow` |
| A project on this flow, new feature | `grill-me`, then `to-prd` |

## The flow

```text
0 IDEA          product-discovery                     only when no stories exist
1 REQUIREMENTS  grooming → us-ac-formatter
2 DESIGN        technical-spec → api-spec
3 PLAN          task-breakdown → deployment-plan
4 SETUP         tech-lead-setups → coding-standard → github-project-init
5 HANDBOOK      project-docs → init-claude
6 BUILD         tdd → code-review                     per card, per pull request
7 CHANGE        grill-me → to-prd → to-issues → 6     new feature on a running project
8 ADOPT         adopt-flow → missing parts of 2 to 5 → 7
  LATER         troubleshooting                       once real incidents exist
```

## Skills

| Phase | Skill | Reads | Writes |
| --- | --- | --- | --- |
| 0 | `product-discovery` | The idea, by interview | A table of user stories, acceptance criteria, and sprints |
| 1 | `grooming` | That table | A question file for the BA/PO, or refined stories |
| 1 | `us-ac-formatter` | The refined table | `docs/business/`: stories, sprints, Gherkin AC |
| 2 | `technical-spec` | `docs/business/` | `docs/technical-specs/`, including security and a threat model |
| 2 | `api-spec` | The technical specs | `docs/api-specs/` |
| 3 | `task-breakdown` | Business docs and specs | `docs/TASK_BREAKDOWN.md`: role-assigned cards, wiring cards included |
| 3 | `deployment-plan` | The technical specs | `DEPLOYMENT_PLAN.md` |
| 4 | `tech-lead-setups` | Specs and the task breakdown | The scaffold, local tooling, and the test harness with one e2e smoke flow |
| 4 | `coding-standard` | The code and the specs | `CODING_STANDARD.md`, `CODE_REVIEW_CHECKLIST.md` with security items |
| 4 | `github-project-init` | Task breakdown, standard, deployment plan | Issues, board, branches, templates, CI workflows |
| 5 | `project-docs` | The code and the docs | `README.md`, `GLOSSARY.md`, development and onboarding guides |
| 5 | `init-claude` | All of the above | `CLAUDE.md` |
| 6 | `code-review` | The pull request, standard, checklist | A review with checked findings |
| 7 | `to-prd` | A `grill-me` decision log | New stories and AC in `docs/business/`, a parent issue |
| 7 | `to-issues` | New stories and AC | New cards in the task breakdown, one issue per card |
| 8 | `adopt-flow` | The existing repository | An audit of missing docs, then runs the skills that write them |
| Later | `troubleshooting` | Architecture and deployment plan | `TROUBLESHOOTING.md` |

## Rules every skill follows

- A fact lives in one document. Other documents link to it.
- A skill that makes decisions interviews the user first, one question at a time, each with a recommended answer.
- A skill that runs on an existing project reads the code and describes what is there.
