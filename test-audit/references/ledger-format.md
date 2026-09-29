# Ledger format

One file per audit: `docs/decisions/<date>-test-audit-<scope>.md`.
`check_ledger.py` reads it.

```markdown
# Test audit: tasks module

Base: 3f2c1a9e0b7d4c6f8a1e2b3c4d5e6f7a8b9c0d1e. Tests in scope: 3.

| Test | Mark | Catches | History | Keeper | Unlocks | Check |
| --- | --- | --- | --- | --- | --- | --- |
| `src/tasks/csv.test.ts` exports visible rows | R | A filter that leaks hidden rows into the file. | Added for AC-29.02. | - | - | - |
| `src/tasks/csv.test.ts` builds header | D | Nothing: the expected header is built by the function under test. | Added with the first CSV commit. | `src/tasks/export.routes.test.ts` returns the CSV header | `buildHeaderForTest` export | `bun test src/tasks` |
| `src/tasks/guard.test.ts` rejects other project | F | Nothing today: a refusal from the auth guard passes it first. | Added in the scope fix. | - | - | `bun test src/tasks/guard.test.ts` |
```

## Columns

| Column | Rule |
| --- | --- |
| Test | The file in backticks, then the test name. |
| Mark | `R`, `F`, `C`, or `D`. |
| Catches | The regression the test can detect. For D or F, what it misses, starting with `Nothing`. |
| History | Why the test exists, from `git log`. |
| Keeper | For C and D: the test that keeps the contract, as its file in backticks and its name, or `None needed: <reason>`. Otherwise `-`. |
| Unlocks | The production or test-support code the edit deletes, or `-`. |
| Check | For F, C, and D: the command that runs the keeper. Otherwise `-`. |

The ledger is ASCII only. There is one row per test in scope.
