# Task breakdown layout

The board is a folder. `recompute_summary.py` writes the Summary table.

```text
docs/task-breakdown/
  _index.md              how to use the board, and the Summary table, which links each sprint file
  team-and-process.md    engineer composition, work model, Definition of Done (per card)
  sprint-0.md            one file per sprint, named by the sprint number
  sprint-1.md
```

## `sprint-N.md`

```markdown
# Sprint N: <name>

Stories: US-01, US-02
Goal: <one line>

### Backend

| Card ID | PM Card Title | Task Description | AC | Owner | Est | Docs |
| --- | --- | --- | --- | --- | --- | --- |
| BE-SN-01 | ... | ... | AC-01.01 | BE1 | 2d | ../technical-specs/05-module-definitions.md#51-... |

### Frontend

| Card ID | PM Card Title | Task Description | AC | Owner | Est | Docs |
| --- | --- | --- | --- | --- | --- | --- |
```

- Wiring cards sit in the Backend or Frontend table of the role that owns them, not in a separate section.
- Card IDs: `<BE|FE|TL|DB>-S<sprint>-<NN>`, zero-padded `NN`, sequential within role and sprint. Keep existing IDs when you update a board, even when a gap appears: the script warns about gaps but never asks you to renumber.
- `Est` is in developer-days, written like `2d` or `1.5d`.

## `_index.md`

```markdown
# Task Breakdown

<how to read and update the board, in a few lines>

- [Team and process](team-and-process.md)

## Summary

| Sprint | Focus | BE cards | FE cards | BE Est | FE Est |
| ------ | ----- | -------- | -------- | ------ | ------ |
| [S1](sprint-1.md) | ... | 4 | 3 | 6d | 5d |
```

## Older projects

An older project keeps the whole board in one `docs/TASK_BREAKDOWN.md`, with a
`## Sprint N: <name>` section per sprint and `## Definition of Done` and
`## Summary` at the end. Both scripts read that shape too. To migrate, move each
sprint section into `sprint-N.md`, the team, work model, and Definition of Done
into `team-and-process.md`, and rerun `recompute_summary.py --write`.
