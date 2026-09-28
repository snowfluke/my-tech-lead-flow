# Triage log format

One file per round: `docs/decisions/<date>-<round>-triage.md`, for example
`docs/decisions/2026-10-02-sit-1-triage.md`. `check_triage.py` reads it.

```markdown
# SIT round 1 triage

Source: sit-1-results.csv, 2026-10-02. Items: 4.

| Item | Summary | Class | AC | Target | Why |
| --- | --- | --- | --- | --- | --- |
| SIT-01 | Export ignores the status filter | Bug | AC-29.02 | #57 | The THEN clause says visible rows only. The file has every row. |
| SIT-02 | Export should include comments | Change | - | #58 | No AC covers comments in the export. |
| SIT-03 | Login times out after 5 minutes | Duplicate | AC-02.04 | #41 | #41 reports the same timeout. |
| SIT-04 | Date shows in UTC | Not a defect | AC-29.05 | - | AC-29.05 says dates are in UTC. |
```

## Columns

| Column | Rule |
| --- | --- |
| Item | The tester's own item ID. Keep it verbatim. |
| Summary | One line, 12 words at most. |
| Class | `Bug`, `Change`, `Duplicate`, `Later`, or `Not a defect`. |
| AC | The AC ID. A Bug must have one. Use `-` when no AC applies. |
| Target | `#n` for every class except Not a defect, which has `-`. |
| Why | One sentence. A Bug quotes what the THEN clause says against what happened. A Not a defect row quotes the AC or names the setup fault. |

The log is ASCII only. There is one row per input item, so the row count
matches the item count.
