# Claude Code Skills

Personal skill library for Claude Code. The core of this repository is a
**technical lead pipeline**: a sequence of skills that takes a product idea
from raw user stories all the way to a reviewed, documented, deployable
codebase. Each stage is a skill that reads the artifacts produced by the
previous stage and writes the next one, so the project documentation stays
consistent and every decision is traceable back to an acceptance criterion.

## The technical lead pipeline

The pipeline runs in order. Steps 1 and 3 are manual (the human supplies or
edits the source material); every other step is a skill invoked with `/<name>`.

| Step | Stage | Skill | Produces |
| ---- | ----- | ----- | -------- |
| 1 | Capture requirements | (manual) | A Markdown table of user stories, acceptance criteria, and a sprint breakdown |
| 2 | Groom | `grooming` | Technical questions for the BA/PO, an INVEST readiness verdict, and concrete add/remove/edit suggestions for the US and AC |
| 3 | Refine | (manual) | Edits to the US and AC based on grooming output |
| 4 | Format | `us-ac-formatter` | `docs/business/`: `user-story.md`, `sprint-breakdown.md`, and per-sprint Gherkin acceptance criteria |
| 5 | Specify | `technical-spec` | `docs/technical-specs/`: numbered `NN-topic.md` files plus `_index.md`, including ad-hoc trailing specs. Grills on tech stack and tooling first |
| 6 | Plan work | `task-breakdown` | `docs/TASK_BREAKDOWN.md`: sprint-by-sprint, role-assigned cards, with frontend/backend wiring as its own owned card |
| 7 | Set up project | `tech-lead-setups` | The Sprint 0 scaffold: folder structure, architectural patterns, commit hooks, tooling config, and endpoint/page stubs returning mock responses. Grills first, then executes |
| 8 | Set standards | `coding-standard` | `CODING_STANDARD.md` and `CODE_REVIEW_CHECKLIST.md` |
| 9 | Plan deployment | `deployment-plan` | `DEPLOYMENT_PLAN.md`: an operational runbook. Grills on infrastructure first |
| 10 | Orient newcomers | `project-docs` | `README.md`, `GLOSSARY.md`, `DEVELOPMENT_SCENARIO_GUIDE.md`, `ONBOARDING_GUIDE.md` |
| 11 | Document failures | `troubleshooting` | `TROUBLESHOOTING.md`: symptom-indexed guide, scaffolded from the architecture seams |
| 12 | Init agent manual | `init-claude` | `CLAUDE.md`: a dense agent operating manual distilled from the specs, standard, task breakdown, and deployment plan |
| 13 | Build | (manual + skills below) | The implementation |
| 14 | Review | `code-review` | A structured PR review against the standards, run in an isolated git worktree |

### How the stages connect

- `grooming`, `us-ac-formatter`, and `technical-spec` all treat `docs/business/`
  as the product source of truth.
- `technical-spec` is the architectural keystone: the tech stack, data model,
  and module boundaries it fixes are what `task-breakdown`, `tech-lead-setups`,
  `coding-standard`, and `deployment-plan` build on.
- `tech-lead-setups` reads the technical specs to build the scaffold that
  `coding-standard` then describes and `code-review` enforces.
- `coding-standard` writes the two documents that `code-review` consumes as its
  source of truth.
- `deployment-plan` writes the runbook that `troubleshooting` references rather
  than duplicates.
- `init-claude` runs last, distilling the specs, standard, task breakdown, and
  deployment plan into the `CLAUDE.md` an agent reads before building.
- Every doc cross-links its siblings instead of restating their content, so
  facts live in exactly one place.

## Supporting skills

General-purpose skills that assist the pipeline at any stage:

- `grill-me`, `grill-with-docs`: stress-test a plan or design before building.
- `diagnose`: disciplined debugging loop. Feeds confirmed incidents back into
  `troubleshooting`.
- `tdd`: red-green-refactor build loop.
- `to-prd`, `to-issues`, `triage`: convert context into tracked work.
- `improve-codebase-architecture`, `zoom-out`, `prototype`, `simplify`.
- `git-commit`, `setup-pre-commit`, `git-guardrails-claude-code`.
- `stop-slop`: remove AI writing patterns from prose.
- `handoff`, `caveman`, `skill-creator`, `write-a-skill`.
