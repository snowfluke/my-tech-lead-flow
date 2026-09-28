# Output layout

Both documents are folders with the numbered files below. Keep every file and its number, because other documents link to sections by
number. A section that does not apply to this project holds one line:
`Not applicable: <reason>`.

## `docs/coding-standard/`

```text
_index.md                       stack summary, verification commands, table of contents
01-language-and-types.md
02-naming.md
03-structure-and-layering.md
04-file-and-function-size.md
05-error-handling.md
06-concurrency-and-transactions.md
07-dependencies-and-tooling.md
08-tests.md
09-security-and-secrets.md
10-comments-commits-and-docs.md       includes the `pr-hygiene` block that hooks and CI read
11-formatting.md
```

Inside file `NN`, number the headings `## N. <Title>` and `### N.1 <Rule group>`,
so a rule has one stable anchor. Each rule is an imperative sentence, a
one-line rationale, and a correct and incorrect example in the project's
language. Mark a rule the linter, formatter, or CI already enforces as
**(enforced)**.

## `docs/code-review-checklist/`

```text
_index.md                       how to walk it, what CI already covers, table of contents
01-scope.md
02-architecture.md
03-correctness.md
04-security.md
05-api-contract.md
06-tests.md
07-commits-and-docs.md
```

The files follow the order a reviewer reads a pull request. Every item is one
binary line that links to the rule behind it:

```markdown
- [ ] Handlers contain no business logic. See [3.2](../coding-standard/03-structure-and-layering.md#32-handlers).
```

`04-security.md` has one item per security control that the technical spec
defines, and names the control ID:

```markdown
- [ ] SEC-03: Every state-changing route checks the caller's role. See [SEC-03](../technical-specs/07-security.md#sec-03).
```

Tag an item that CI already checks with **(CI)**, so the reviewer spends time
on what tools cannot catch.

## Existing single-file documents

An older project may have `CODING_STANDARD.md` (or `CODING_STANDARDS.md`) and `CODE_REVIEW_CHECKLIST.md`
as single files. `code-review` reads both shapes. To migrate, move each `##`
section into its own numbered file, keep the wording, and fix every link that
pointed into the old file.
