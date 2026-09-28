# Bug issue format

Title: `<summary>` in 12 words or fewer, for example `Export ignores the status filter`.

```markdown
Source: SIT round 1, item SIT-01.
AC: [AC-29.02](<link to the AC in docs/business/>)

## Expected

<the THEN clause of the AC, verbatim>

## Actual

<what happened, from the tester's result>

## Steps

1. <step>
2. <step>

## Environment

<build or commit, environment name, browser or device>
```

The Expected section is the AC text, not the tester's words. `work-card`
reads this issue as a Fix card, and `lead-review` quotes the same AC as the
Rule. A Later item uses the same format.
