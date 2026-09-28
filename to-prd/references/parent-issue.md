# Parent issue body

The body `to-prd` step 6 writes to `/tmp/prd-<slug>.md` before `gh issue create`, or saves as `docs/decisions/<YYYY-MM-DD>-prd-<slug>.md` when the project files no issues.

```markdown
## Problem
<one paragraph, from the user's side>

## Solution
<one paragraph, from the user's side>

## Stories and criteria
- US-XX <title>: AC-XX.01, AC-XX.02 (<link on the default branch: the sprint file in docs/business/, or the older AC file>)

## Spec impact
- <spec section>: <what changes>

## Out of scope
- <item>

## Decisions
<link to the decision log, if one exists>
```
