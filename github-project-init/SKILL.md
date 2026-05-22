---
name: github-project-init
description: Stand up the GitHub project from the task breakdown, after coding standards are set. Converts every TASK_BREAKDOWN card into an issue (assigned to the right teammate, labelled, milestoned per sprint, placed in the board Backlog), creates the Projects v2 Kanban board, the dev/test/main branches with protection, issue and pull-request templates, CI quality and build workflows, dependabot, and a release template. Asks each role (TL, BE1, FE1, ...) for their GitHub username first. Use when the user wants to initialize a GitHub project, create issues from the task breakdown, set up the kanban board, repo templates, branches, or CI workflows.
---

# GitHub Project Init

Turn the planned work into a live GitHub project: issues, board, branches, templates, and CI. This runs **after `coding-standard`** (the PR template and CI quality gate reference the checklist) and reads `docs/TASK_BREAKDOWN.md` as the issue source.

This skill performs many outward-facing, hard-to-reverse actions (creating dozens of issues, branches, a board). Work in two phases: **gather and confirm the full plan, then execute.** Never bulk-create before the user has approved the plan and the issue count.

## Prerequisites

- `gh` authenticated with repo write access: `gh auth status`. If not, ask the user to run `gh auth login`.
- A GitHub repository exists for this project. If not, confirm and create it (`gh repo create`).
- `docs/TASK_BREAKDOWN.md` exists (run `task-breakdown` first if not) and `CODING_STANDARD.md` / `CODE_REVIEW_CHECKLIST.md` exist (the templates and CI reference them). Read `docs/technical-specs/` and `DEPLOYMENT_PLAN.md` for the verification commands and the branch/deploy model.

## Phase 1 — Gather and confirm

1. **Resolve the repo.** `gh repo view --json nameWithOwner,defaultBranchRef`. Confirm owner/name with the user.
2. **Collect GitHub usernames per role.** From `TASK_BREAKDOWN.md` the roles are placeholders (`TL`, `BE1`, `FE1`, `FE2`, ...). Ask the user for each one's GitHub username (use `AskUserQuestion`), allowing "none" so that role's issues stay unassigned. Build a `role -> @username` map; this drives issue assignees.
3. **Confirm the label vocabulary.** Propose the set in `<labels>` and let the user adjust before creating.
4. **Confirm the board columns.** Propose `Backlog, Ready, In Progress, In Review, Done`; every issue starts in **Backlog**.
5. **Confirm the branch model.** `dev`, `test`, `main`; feature branches target `dev`, `dev` promotes to `test`, `test` releases to `main` (match `DEPLOYMENT_PLAN.md`). Confirm the default branch (usually `dev`) and which branches get protection.
6. **Confirm CI shape.** A quality workflow (lint, format, type-check, test, build on PRs and pushes to the long-lived branches) using the project's real commands, and a build/deploy workflow that is manual (`workflow_dispatch` with an environment selector) plus on release. Confirm the verification commands from the standard/specs.
7. **Summarize and get the go-ahead.** State the counts (N issues across M sprints, the branches, the files to be committed) and confirm before executing. This is the gate.

## Phase 2 — Execute

Run in this order so dependencies exist before they are referenced. Prefer `gh` and `gh api` (remote operations) so nothing depends on a local push. Make every step idempotent: check existence before creating, so a re-run repairs rather than duplicates.

### A. Labels

Create the agreed set (idempotent: `gh label create <name> --color <hex> --description <d> --force`). See `<labels>`.

### B. Branches and protection

- Get the base SHA: `gh api repos/{owner}/{repo}/git/refs/heads/{default} --jq .object.sha`.
- Create `dev`, `test`, `main` if missing via the refs API (this is not a `git push`, so it works even under a push-blocking hook):
  `gh api -X POST repos/{owner}/{repo}/git/refs -f ref=refs/heads/dev -f sha=<sha>`.
- Set the default branch: `gh api -X PATCH repos/{owner}/{repo} -f default_branch=dev`.
- Protect `main` and `test` (require the CI quality check and at least one review) via `gh api -X PUT repos/{owner}/{repo}/branches/{b}/protection ...`. Confirm the exact rules with the user.

### C. Repo files

Generate these from the project's real values (commands, checklist, sprints), then commit them. Open a PR into `dev` rather than committing to a protected branch. If a local push is blocked by a guardrail hook, hand the push command to the user.

- `.github/ISSUE_TEMPLATE/feature.md` and `bug.md` (and `config.yml`): fields for the linked US/AC ids, task id, description, and definition of done.
- `.github/PULL_REQUEST_TEMPLATE.md`: task id, US/AC covered, target branch, what/why/how-to-test, and the self-review attestation that points at `CODE_REVIEW_CHECKLIST.md`.
- `.github/workflows/ci.yml`: the quality gate. Run the project's type-check, lint, format-check, test, and build on `pull_request` and on push to `dev`/`test`/`main`. Use the detected package manager and commands; do not hard-code a stack.
- `.github/workflows/build.yml` (or `deploy.yml`): `workflow_dispatch` with an environment input, plus a `release: published` trigger for production. Mirror the deploy policy in `DEPLOYMENT_PLAN.md`.
- `.github/dependabot.yml`: the ecosystem(s) present in the repo, weekly, grouped where sensible.
- `.github/release.yml`: auto-generated release-notes categories mapped to the labels.

### D. Milestones

One milestone per sprint from `TASK_BREAKDOWN.md` (`Sprint 1 — <focus>`, ...):
`gh api -X POST repos/{owner}/{repo}/milestones -f title="..." -f description="..."`.

### E. Project board

- Create the Projects v2 board: `gh project create --owner {owner} --title "<repo> delivery"`.
- Ensure the `Status` field has the agreed columns and that `Backlog` is the default.
- Items are added in step F and set to `Backlog`.

### F. Issues from the task breakdown

Parse the card tables in `TASK_BREAKDOWN.md`. For each card create one issue:

- **Title**: `<Card ID> <PM Card Title>` (e.g. `BE-S1-08 Implement real POST /work-orders`).
- **Body**: the Task Description, the AC ids it satisfies (link to `docs/business/`), the Docs refs, and the Est. Note wiring cards explicitly.
- **Labels**: area from the Card ID prefix (`BE`->`area:backend`, `FE`->`area:frontend`, `TL`/`DB`->`area:infra`), a `type:*`, the `sprint:<n>`, and `wiring` for wiring cards.
- **Assignee**: the `role -> @username` map (skip if "none").
- **Milestone**: the sprint milestone.

Then add the issue to the board and set its status to `Backlog`:
`gh issue create --title "..." --body-file <tmp> --label ... --assignee ... --milestone "..."` then `gh project item-add` and set the status field.

Create them in a loop. For a large breakdown, confirm the count first and report progress as you go. Skip cards whose issue already exists (match by title) so a re-run is safe.

### Report

When done, report what was created: issue count per sprint, the board URL, the branches and protection, and the PR that adds the `.github` files. List anything skipped (existing issues, unassigned roles).

<labels>

Propose this default set (color is a suggestion):

- Type: `type:feature`, `type:bug`, `type:chore`, `type:refactor`, `type:docs`
- Area: `area:backend`, `area:frontend`, `area:infra`, `area:docs`
- Sprint: `sprint:0` ... `sprint:N` (one per sprint in the breakdown)
- Flow: `wiring` (frontend/backend integration cards), `blocked`, `needs-review`
- Priority (optional): `priority:high`, `priority:medium`, `priority:low`

</labels>

## Safety

- Confirm the plan and the issue count before creating anything. Bulk issue creation is tedious to undo.
- Idempotent throughout: check before create; a second run repairs gaps instead of duplicating.
- Do not commit directly to a protected branch; open a PR into `dev`.
- If a push-blocking guardrail hook is active, the remote `gh`/`gh api` operations still work; only local `git push` for the `.github` files needs to be handed to the user.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
