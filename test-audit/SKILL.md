---
name: test-audit
description: Audit a project's existing tests for low value. Finds tests that match the junk patterns, duplicate a stronger test, or couple to the implementation, and the test-only production seams they keep alive. Records evidence for every test in a checked ledger before any edit, then deletes, repairs, or consolidates one coherent batch per PR. Use when the user wants to clean up, prune, sweep, or audit tests, reduce test maintenance, find useless or AI-generated tests, or asks "which of these tests matter".
---

# Test Audit

Optimize for confidence, not for deletion count. A test earns its place when it
protects a behaviour, a credible regression, or a contract that matters on its
own. The rules are the project's test rules in its coding standard, including
the junk patterns. If the project has none, use the baseline in
`coding-standard`'s `references/baseline-rules.md`, and tell the user to adopt
it.

For one whole subsystem in one PR, follow [references/campaign.md](references/campaign.md)
instead of step 3 to step 5.

## 1. Scope

Agree the scope with the user: one module, one folder, or one pattern across
the repo. Pin the base commit: `git rev-parse HEAD`. Run the scope's tests once
on it and record each file's result. A test that fails on the base is a
possible product bug. Reproduce it and report it; never delete it.

## 2. Discover, read only

Edit nothing in this step. Read `CLAUDE.md` or `AGENTS.md`, then the test rules.
For each test in scope, read the whole test, the production code it covers, its
callers, the tests next to it, and `git log` for why it exists. When a test
claims behaviour of a dependency, read the dependency's source or types.

Hunt for the junk patterns. Prefer a few candidates you are sure of over a long
list you guess at. Static or slow is not a reason to delete.

## 3. Write the ledger

Write one row per test in scope to `docs/decisions/<date>-test-audit-<scope>.md`
in the format of [references/ledger-format.md](references/ledger-format.md).
Mark each test:

| Mark | Meaning | The row must name |
| --- | --- | --- |
| R | Retain | The regression it catches |
| F | Fix the assertion, keep the contract | What the assertion misses today |
| C | Consolidate into another test | The keeper test that absorbs it |
| D | Delete | The keeper test that still proves the contract, or why no contract exists |

Judge a test by its assertions, not by its name. Then check the ledger:

```bash
python3 <this skill's dir>/scripts/check_ledger.py docs/decisions/<date>-test-audit-<scope>.md
```

Show the C and D rows to the user and get approval before any edit.

## 4. Edit one batch

Take one coherent batch: one production owner and its tests. In the same
change, delete the test-only exports, flags, wrappers, and dead production code
the batch unlocks. Do not keep aliases for them. Do not add a replacement test
that restates the same implementation.

For every F and C row, prove the keeper: break the production code once, watch
the keeper fail, then restore the code byte for byte.

## 5. Check and hand off

Run the scope's tests, the project's full check, and `git diff --check`. Run
`git diff --numstat` and report production lines and test lines separately.
Commit with `git-commit` and open the PR with `open-pr`. The PR body links the
ledger.

Report:

- the junk patterns removed and their counts;
- the production code the batch deleted;
- tests kept that looked like junk, and why each stays;
- base failures found, as bugs with their reproduction;
- the next batch, if the scope has more.

Adapted from OpenClaw's test-audit skill. See [references/LICENSE-openclaw.md](references/LICENSE-openclaw.md).
