---
name: security-standard
description: Write the project's security standard (docs/security-standards/), the audit view of its security design. Maps each risk in the OWASP API Security Top 10, the OWASP Top 10 for web applications, and the ASVS chapters to the project's controls, with a status and the file that proves it. Adds what must be true before the app faces the internet, what is deliberately not done, and what the product can and cannot claim. A script checks that every cited path exists and every open row names a card or issue. Use before the first release and again before each release, or when the user asks for a security standard, a security checklist, an OWASP mapping, or a security audit document.
---

# Security Standard

The technical spec's security file is the design: its threat model and its
`SEC-NN` controls. The review checklist checks each control in each PR. This
document is the audit view: it takes the standard risk lists and shows, row by
row, what the project does and where. A reader checks a row by opening its
file. A row with no file is only a claim.

## 1. Read

- **Controls.** The security file in `docs/technical-specs/` (usually `07-security.md`) and its `SEC-NN` IDs. If the spec has no control IDs, stop and ask the user to run `technical-spec` for that section first.
- **Code.** The auth, validation, rate-limit, header, logging, and secrets code the controls name. Read the code; do not trust the spec's description of it.
- **Delivery.** `.github/workflows/`, `.github/dependabot.yml`, the lockfile, `Dockerfile`, and `docs/deployment-plan/`.
- **Existing document.** If the project already has a security standard in its own layout, it is the source of truth. Update it in that layout.

## 2. Pin the lists

Ask the user which lists apply and which edition of each. Suggest the editions
in [references/lists.md](references/lists.md). Tell the user to check
owasp.org for a newer edition before pinning one. Write the pinned editions in
`_index.md`. Never mix editions in one file.

## 3. Map each row

Write each list as a table in the layout of
[references/layout.md](references/layout.md). For each risk:

| Status | When | Where holds |
| --- | --- | --- |
| Done | A control covers the risk in code or config. | The paths that prove it, in backticks, and the `SEC-NN` IDs. |
| Partial | A control covers part of the risk. | The paths, then the card or issue that closes the rest. |
| Not done | No control covers the risk yet. | The card or issue that adds it. |
| Not applicable | The risk cannot occur in this product. | The reason, in one sentence. |

Mark a row Done only when you opened the file and saw the control. For a
Partial or Not done row with no card or issue, file one with `triage` as a
Later item with the `backlog` label, then cite it.

## 4. Write the closing files

- **Before exposure.** The conditions that must hold before an instance faces the internet, in order. Each is a row with a status and a `Where`.
- **Not done on purpose.** Each control the team decided not to build, with the reason. It saves the next auditor from asking again.
- **Claims.** What the product can claim against a standard, and what it cannot. A product is not ISO/IEC 27001 certified: an organization is. Say which duties stay with the operator.

## 5. Check

```bash
python3 <this skill's dir>/scripts/check_security.py docs/security-standards --spec docs/technical-specs
```

It fails on a missing section file, a status outside the four, a Done row
without an existing path, an open row without a card or issue, a Not
applicable row without a reason, an unknown `SEC-NN` ID, and non-ASCII text.
Fix every error, then hand the folder to `git-commit`.

Run the skill again before each release. Update the rows; do not start a
second document.
