---
name: to-issues
description: Turn new user stories and acceptance criteria, usually from to-prd, into task-breakdown cards (backend, frontend, and a wiring card where the seam needs one) added to docs/task-breakdown/, then file one issue per card the way github-project-init does, with the role's assignee, labels, sprint milestone, board status, and estimate, each linked to the parent issue. Use when the user wants to break a feature or PRD into issues or tickets on a project that is already running.
---

# To Issues

The mid-project counterpart of `task-breakdown` plus `github-project-init`. It
adds cards to an existing board in the same format, so the task breakdown and
the GitHub board keep matching.

## 1. Read the input and the board

- **Input.** A parent issue number or URL from `to-prd`, or a list of US IDs. Read the parent issue with `gh issue view <n>`.
- **Criteria.** Read those US and AC in the business docs: `docs/business/`, or the older files `to-prd` wrote them into.
- **Board.** Read `docs/task-breakdown/`: the roles in `team-and-process.md`, the target `sprint-N.md`, and the last card number per role in that sprint. An older project keeps all of it in one `docs/TASK_BREAKDOWN.md`.
- **Specs.** Read the spec sections the parent issue lists under "Spec impact".

If the board exists in its own layout (for example grouped by module or
priority, with its own ID scheme and status markers), it is the source of
truth. Add cards in that layout, with its ID scheme and markers.

If the project has no task breakdown in any form (a running project adopting
this flow), create `docs/task-breakdown/` in the layout of `task-breakdown`'s
`references/layout.md`: `_index.md`, and `team-and-process.md` with the team
the user confirms. Add no past sprints. The new cards start the first sprint
file.

## 2. Draft the cards

Read the `task-breakdown` skill and follow its `<rules>`, `<wiring-cards>`, and
`references/layout.md`. In short:

- Split the work into backend and frontend cards. One card is one owner and one verifiable slice.
- Add a wiring card where the seam between them is not trivial. The owner of the card that lands last owns it.
- Give each card the next free Card ID for its role and sprint, the AC IDs it satisfies, an owner role, an estimate in developer-days, and the spec sections it follows.
- Never cite an AC that does not exist. If work needs a missing AC, stop and point the user at `to-prd` or `grooming`.

Show the cards as the table they will become. Ask only about owners and
estimates the input leaves open. Get the user's approval.

## 3. Write the board

Add the cards where the board keeps them: `docs/task-breakdown/sprint-N.md`
(create the file if the sprint is new), or the older single file. Edit in
place and leave other cards alone. Then run the `task-breakdown` scripts on
the board you edited (`<board>`) and the business docs you read (`<business>`,
a folder or an older AC file):

```bash
python3 <task-breakdown dir>/scripts/recompute_summary.py <board> --write
python3 <task-breakdown dir>/scripts/check_ac_refs.py <board> --business-dir <business>
```

`recompute_summary.py` refuses a board in another layout and writes nothing.
Then update that board's summary by hand. Fix every error the scripts report. Hand the file to `git-commit`.

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
