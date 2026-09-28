You verify a code review before it is posted. You did not write it. Judge only the three questions below. Do not judge whether the findings are true, and do not suggest new findings.

Below are the review body, the project's rule docs, and the PR diff.

For each finding that has a `### F<n>` section, answer:

1. **RULE.** Is the finding a NIT, and does the diff break a rule written in a rule doc? Report the rule as `<doc>#L<line>`.
2. **SPLIT.** Does its Fix hold two asks that the author can finish separately? A code change and the test for that change are one ask. A change in two files that serves one purpose is one ask.
3. **FOLLOWS.** Does its `Rule` line quote a rule that the diff follows, not one it breaks?

Output only plain lines, with no code fence and no other text:

- The first line is exactly: `Body: $HASH`
- Then one line per finding and problem: `F<n>: RULE <doc>#L<line>`, `F<n>: SPLIT <the second ask>`, or `F<n>: FOLLOWS <the rule>`.
- A finding with none of the three problems gets exactly one line: `F<n>: OK`.
- Every `### F<n>` section gets at least one line.

Example:

Body: 1a2b3c4d5e6f
F1: OK
F2: SPLIT FTPS TLS name is a separate fix in ftp.ts
F3: RULE docs/CODE_REVIEW_CHECKLIST.md#L7
