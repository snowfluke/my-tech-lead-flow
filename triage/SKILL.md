---
name: triage
description: Sort the results of a SIT or UAT round, bug reports, and late requests on a running project. Each item becomes a bug issue, a change for to-prd and to-issues, a duplicate, a backlog issue, or an answered non-defect, and a triage log records every item. Never rebuilds the task breakdown and never edits an AC. Use when the user shares SIT or UAT results, a tester's findings sheet, a batch of bug reports, or asks to "triage", "file the SIT bugs", or "put this in the backlog".
---

# Triage

A test round adds work to a running project. Triage sorts that work. It adds
issues and hands changes to the change lane. It never runs `task-breakdown`
again, never renumbers a card, and never edits an AC.

## 1. Read the input and the project

- **Results.** A CSV export, a markdown table, a pasted list, or a spreadsheet. Read an `.xlsx` file with the `xlsx` skill when it is installed. Without it, ask for a CSV export of the sheet that holds the results. Do not guess the columns: ask which column holds the item ID, the steps, the expected result, and the actual result.
- **Round.** The round name, for example `sit-1` or `uat-2`, and its date.
- **Criteria.** The ACs in `docs/business/`, or the older AC file.
- **Board.** `docs/task-breakdown/`, or the older single file. Read which cards each AC belongs to.
- **Issues.** The project's labels, milestones, and open issues: `gh label list`, `gh issue list --state all --limit 500`.

Count the items. Every item gets one row in the log, so the count is the
check that none is lost.

## 2. Classify each item

| Class | When | Target |
| --- | --- | --- |
| Bug | The app breaks the THEN clause of an existing AC. | A new issue, `#n`. |
| Change | No AC covers what the tester expected, or the tester expects something an AC does not say. | The `to-prd` parent issue, `#n`. |
| Duplicate | An open issue already reports it. | That issue, `#n`. |
| Later | Real, but the user moves it out of this release. | A new issue with the `backlog` label, `#n`. |
| Not a defect | The app does what the AC says, or the cause is the test setup. | `-`, and the reason quotes the AC or names the setup fault. |

A Bug always cites the AC it breaks. If you cannot quote the THEN clause it
breaks, it is not a Bug: it is a Change. Bug or Change is the product owner's
call when the AC is unclear. Ask the user; do not decide it yourself.

Show the classes as the log table ([references/log-format.md](references/log-format.md))
with Target still empty. Get the user's approval. The user may move any item
to Later.

## 3. File the work

State the number of issues you will create and get the go-ahead.

- **Bug.** Create one issue per bug with the body in [references/issue-format.md](references/issue-format.md). Labels: `type:bug`, `source:<sit|uat>`, and the area of the card that owns the AC. Milestone: the current sprint. Skip it when an issue with the same title exists.
- **Duplicate.** Comment on the existing issue with the tester's item ID and the round.
- **Later.** Create the issue in the same format. Labels: `backlog` and `source:<sit|uat>`. No milestone.
- **Change.** Hand all Change items to `to-prd` in one run. It writes the new or changed AC and the parent issue. Then `to-issues` adds the cards to the board. A large change goes through `grill-me` first.
- **Not a defect.** Create no issue. The log row carries the answer for the tester.

If a label is missing, create it with the colours from
`github-project-init`'s `references/labels.md`.

## 4. Write the log and check it

Fill every Target and write the log to
`docs/decisions/<date>-<round>-triage.md`. Then check it against the item
count:

```bash
python3 <this skill's dir>/scripts/check_triage.py docs/decisions/<date>-<round>-triage.md --items <count>
```

Fix every error. Hand the log to `git-commit`.

## 5. Report

Report one line per class: the count and the issue numbers. The engineers take
each Bug with `work-card`, which reads an issue as a card.
