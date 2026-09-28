# Tech Lead Skills

Agent skills that take a product from an idea to reviewed code. Each skill reads
the documents the previous one wrote and writes the next, so the specs, the
board, and the code stay in step, and every card traces back to an acceptance
criterion.

## Install

Install with the [`skills` CLI](https://github.com/vercel-labs/skills). It works
with Claude Code, opencode, Codex, and other agents.

| Goal | Command |
| --- | --- |
| See the skills first | `npx skills add snowfluke/tech-lead-skills -l` |
| Every skill, for you in every project | `npx skills add snowfluke/tech-lead-skills -g --all` |
| Some skills only | `npx skills add snowfluke/tech-lead-skills -g -s lead-review -s coding-standard` |
| Choose interactively | `npx skills add snowfluke/tech-lead-skills` |

The flow also calls these skills from
[engineering-skills](https://github.com/snowfluke/engineering-skills): `grill-me`,
`work-card`, `tdd`, `git-commit`, `open-pr`, `address-review`, `diagnose`, and
`setup-pre-commit`, plus
`git-guardrails-claude-code` on Claude Code. Install them the same way:

```bash
npx skills add snowfluke/engineering-skills -g -s grill-me -s work-card -s tdd -s git-commit -s open-pr -s address-review -s diagnose -s setup-pre-commit
```

### Some skills only: keep the pairs together

A few skills read files from another skill. Install them together, or the
first one fails:

| If you install | Also install |
| --- | --- |
| `api-spec` | `technical-spec` |
| `grooming` | `us-ac-formatter` |
| `tech-lead-setups` | `technical-spec`, `coding-standard` |
| `to-prd` | `us-ac-formatter`, `github-project-init` |
| `to-issues` | `task-breakdown`, `github-project-init` |

### One project only

Run the command in the project root without `-g`. The skills go into the
project, and the CLI writes `skills-lock.json`. Commit both, so the team gets
the same skills.

```bash
cd my-project
npx skills add snowfluke/tech-lead-skills -s lead-review -s coding-standard -a claude-code
```

| Agent flag | Skills go to |
| --- | --- |
| `-a claude-code` | `.claude/skills/` |
| `-a opencode`, `-a codex` | `.agents/skills/` |

A teammate restores the project's skills from the lock file with
`npx skills experimental_install`. That command writes to `.agents/skills/`.
On Claude Code, run the `add` command above with `-a claude-code` instead.

### Edit and publish

Clone this repository and run `./link.sh`. It links every skill into
`~/.claude/skills` (or the directory you pass), so edits land in the clone.
Every script supports `--self-test`:

```bash
for f in */scripts/*.py; do python3 "$f" --self-test; done
```

## Where to start

| Situation | Start with |
| --- | --- |
| An idea, no user stories yet | `product-discovery` |
| User stories exist, new project | `grooming` |
| A running project without these docs | `adopt-flow` |
| A project on this flow, new feature | `grill-me`, then `to-prd` |
| SIT or UAT results, bug reports | `triage` |
| A release is close | `security-standard` |

## The flow

```text
0 IDEA          product-discovery                     only when no stories exist
1 REQUIREMENTS  grooming -> us-ac-formatter
2 DESIGN        technical-spec -> api-spec
3 PLAN          task-breakdown -> deployment-plan
4 SETUP         tech-lead-setups -> coding-standard -> github-project-init
5 HANDBOOK      project-docs -> init-claude
6 BUILD         work-card -> open-pr -> lead-review -> address-review   per card (engineering-skills)
7 TEST          triage -> 6 for bugs, 8 for changes   after each SIT or UAT round
8 CHANGE        grill-me -> to-prd -> to-issues -> 6     new feature on a running project
9 ADOPT         adopt-flow -> missing parts of 2 to 5 -> 8
  RELEASE       security-standard                     before the first release, then each release
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
| 3 | `task-breakdown` | Business docs and specs | `docs/task-breakdown/`: one file per sprint, role-assigned cards, wiring cards included |
| 3 | `deployment-plan` | The technical specs | `docs/deployment-plan/`; on a running project, the deployment as it runs today |
| 4 | `tech-lead-setups` | Specs and the task breakdown | The scaffold, local tooling, and the test harness with one e2e smoke flow; on a running project, only what is missing |
| 4 | `coding-standard` | The code and the specs | `docs/coding-standard/`, `docs/code-review-checklist/` with one item per security control |
| 4 | `github-project-init` | Task breakdown, standard, deployment plan | Issues, board, branches, templates, and the only CI workflows; keeps an existing branch model |
| 5 | `project-docs` | The code and the docs | `README.md`, `docs/GLOSSARY.md`, `docs/development-guide/`, `docs/onboarding/` |
| 5 | `init-claude` | All of the above | `CLAUDE.md` |
| 6 | `lead-review` | The pull request, standard, checklist | A review with checked findings |
| 7 | `triage` | SIT or UAT results, bug reports | Bug and backlog issues, changes handed to `to-prd`, a triage log in `docs/decisions/` |
| 8 | `to-prd` | A `grill-me` decision log | New stories and AC in `docs/business/`, a parent issue |
| 8 | `to-issues` | New stories and AC | New cards in `docs/task-breakdown/`, one issue per card; creates the folder on a running project |
| 9 | `adopt-flow` | The existing repository | An audit of missing docs, then runs the skills that write them |
| Release | `security-standard` | The security spec, the code, CI, deployment | `docs/security-standards/`: each OWASP and ASVS row with a status and the file that proves it |
| Later | `troubleshooting` | Architecture and deployment plan | `docs/troubleshooting/`: one file per seam, by symptom |

## Rules every skill follows

- A fact lives in one document. Other documents link to it.
- A skill that makes decisions interviews the user first, one question at a time, each with a recommended answer.
- A skill that runs on an existing project reads the code and describes what is there.
- A document that already exists in its own layout is the source of truth. A skill extends it in that layout, ID scheme, and language, offers migration once, and never starts a second document of the same kind. The same holds for the project's GitHub conventions: its labels, milestones, and whether it files an issue per card.

## Document layout

No document is one long file. A document with more than one top-level section
is a folder:

```text
docs/<kebab-name>/
  _index.md          header, table of contents, links to sibling documents; no body
  01-<section>.md    one file per section, numbered with two digits
  02-<section>.md
```

`docs/technical-specs/` and `docs/api-specs/` already follow this layout.

- Section numbers are fixed per document type, so links between documents stay valid. A section that does not apply keeps its file with one line: `Not applicable: <reason>`.
- When the unit already has a number, the file takes the unit's name: `docs/task-breakdown/sprint-1.md`.
- The troubleshooting guide is the one exception to fixed numbers: its seam files follow each project's risk order.

Some documents stay single files:

| File | Why |
| --- | --- |
| `README.md` | The repository's front page. It links into the folders. |
| `CLAUDE.md` / `AGENTS.md` | The agent harness reads one file. It links into the folders. |
| `docs/GLOSSARY.md` | One section. |
| `docs/business/user-story.md`, `sprint-breakdown.md` | One list each. The acceptance criteria are already split per sprint. |
| `docs/decisions/<date>-<topic>.md` | One decision log per session, short by design. |

Skill files follow the same idea. `SKILL.md` holds the steps. Templates, format
specs, examples, and long tables live in `references/<topic>.md`, and the step
that needs one links to it.
