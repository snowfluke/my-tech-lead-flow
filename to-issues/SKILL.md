---
name: to-issues
description: Turn new user stories and acceptance criteria, usually from to-prd, into task-breakdown cards (backend, frontend, and a wiring card where the seam needs one) appended to docs/TASK_BREAKDOWN.md, then file one issue per card the way github-project-init does, with the role's assignee, labels, sprint milestone, board status, and estimate, each linked to the parent issue. Use when the user wants to break a feature or PRD into issues or tickets on a project that is already running.
---

# To Issues

The mid-project counterpart of `task-breakdown` plus `github-project-init`. It
adds cards to an existing board in the same format, so `TASK_BREAKDOWN.md` and
the GitHub board keep matching.

## 1. Read the input and the board

- **Input.** A parent issue number or URL from `to-prd`, or a list of US IDs. Read the parent issue with `gh issue view <n>`.
- **Criteria.** Read those US and AC in `docs/business/`.
- **Board.** Read `docs/TASK_BREAKDOWN.md`: the team roles, the sprint section, and the last card number per role in that sprint.
- **Specs.** Read the spec sections the parent issue lists under "Spec impact".

If `docs/TASK_BREAKDOWN.md` does not exist, stop and point the user at
`task-breakdown`.

## 2. Draft the cards

Read the `task-breakdown` skill and follow its `<rules>`, `<wiring-cards>`, and
`<output-format>`. In short:

- Split the work into backend and frontend cards. One card is one owner and one verifiable slice.
- Add a wiring card where the seam between them is not trivial. The owner of the card that lands last owns it.
- Give each card the next free Card ID for its role and sprint, the AC IDs it satisfies, an owner role, an estimate in developer-days, and the spec sections it follows.
- Never cite an AC that does not exist. If work needs a missing AC, stop and point the user at `to-prd` or `grooming`.

Show the cards as the table they will become. Ask only about owners and
estimates the input leaves open. Get the user's approval.

## 3. Write the board

Add the cards to their sprint section in `docs/TASK_BREAKDOWN.md`. Edit in
place and leave other cards alone. Then run the `task-breakdown` scripts:

```bash
python3 <task-breakdown dir>/scripts/recompute_summary.py docs/TASK_BREAKDOWN.md --write
python3 <task-breakdown dir>/scripts/check_ac_refs.py docs/TASK_BREAKDOWN.md --business-dir docs/business
```

Fix every error they report. Hand the file to `git-commit`.

## 4. File the issues

Read the `github-project-init` skill, section "F. Issues from the task
breakdown", and follow it for each new card: title, body, labels, assignee,
milestone, board status `Backlog`, and the `Estimate` field. Two additions:

- Put `Parent: #<n>` as the first line of each body, so GitHub links the card to the parent issue.
- Get the role-to-username map before you create anything. Propose it from the assignees of existing issues with the same Card ID prefix, and let the user confirm it.

State the issue count and get the user's go-ahead first. Create the issues in
dependency order, so a card can name the issue numbers it waits for. Skip a card
whose issue title already exists. Do not edit the parent issue.

Report the new issue numbers per card.
