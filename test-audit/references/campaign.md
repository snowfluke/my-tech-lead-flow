# Campaign mode

A campaign audits one subsystem's whole test surface in one PR. It is heavy:
use it only when the user asks for it. The rules and the ledger of `SKILL.md`
apply. Each step ends on its "Done when". Do not start the next step early.

## 1. Base

Record the subsystem's test and test-support line counts, and each test file's
result at a pinned commit. Keep base failures in their own list. They are often
real bugs, not stale tests.

Done when every test file in scope has a recorded result.

## 2. Lanes

Split the tests into lanes by production owner, not by file name. Include the
subsystem's cases in shared tests and its e2e and QA tests.

Done when every test file belongs to exactly one lane.

## 3. Ledger per lane

Give each lane to its own read-only agent when the harness has subagents.
Otherwise do the lanes one by one. Each lane gets a ledger. A parametrised test
is one row, unless its cases need different marks.

Done when every test in the lane has a mark and passes `check_ledger.py`.

## 4. Layer plan per lane

Read the ledger again and look for a redundant layer: a suite that replays
what a stronger suite already proves. Name the keeper suite for each contract.
Prefer the real boundary with a fake network over a mocked collaborator. Fix
ledger errors you find.

Done when each lane names its retired files, its keeper per contract, the
assertions to move into keepers, and the test-only seams it unlocks.

## 5. Cutover

Edit lane by lane. One person changes a shared test helper at a time. With each
lane, delete the test-only seams it unlocks. Register moved suites in CI.

Done when every lane plan is applied and each lane's keepers pass.

## 6. Preservation review

Have a reviewer in a fresh context compare the deleted tests against the
keepers. The reviewer looks for a contract that lost its only proof, and for a
new assertion that cannot fail. For each restored contract, break the
production code once, watch the keeper fail, and restore the code byte for
byte.

Done when every gap is restored or rejected with evidence, and every restored
contract has a caught break.

## 7. Product bugs

A base failure that survives into a keeper is a bug. Fix it in its own commit.
Prove it with a control run: revert the fix and show the old behaviour. Log
other bugs as issues with `triage`; do not fix them in the campaign.

Done when each fixed bug has a failing control and a passing fix.

## 8. Reconcile

A campaign outlives many commits on the base branch. Merge the base; do not
rebase a long campaign. When the base changed a file the campaign deleted, keep
the deletion and move the new contract into the keeper. Rerun the subsystem's
tests on the merged head.

Report the `SKILL.md` items, plus the line counts before and after (production
apart from tests), the lanes and keepers, the gaps the review found, and the
bugs with their control runs.
