# Security standard layout

```text
docs/security-standards/
  _index.md                  the pinned editions, links to each file, and to the spec's security file
  01-owasp-api-top-10.md
  02-owasp-web-top-10.md
  03-asvs.md
  04-before-exposure.md
  05-not-done.md
  06-claims.md
```

The numbers are fixed. A file that does not apply keeps one line:
`Not applicable: <reason>`. For example, a product with no browser client
marks `02-owasp-web-top-10.md` not applicable.

## Risk tables (01 to 04)

```markdown
# OWASP API Security Top 10 (2023)

| # | Risk | Control | Status | Where |
| --- | --- | --- | --- | --- |
| API1 | Broken object level authorization | SEC-03 | Done | `src/http/auth.ts` checks the project scope on every project route. `src/http/auth.test.ts` pins it. |
| API4 | Unrestricted resource consumption | SEC-07 | Partial | `src/http/limits.ts` caps the body size. Upload limits are BE-S4-02. |
| API6 | Unrestricted access to sensitive business flows | - | Not done | #88 |
| API9 | Improper inventory management | - | Not applicable | The API has one version and one prefix, and the OpenAPI document is generated from the routes. |
```

- `#` is the list's own ID. `Risk` is the list's own name for it.
- `Control` holds the `SEC-NN` IDs from the technical spec, or `-`.
- `Status` is one of `Done`, `Partial`, `Not done`, `Not applicable`.
- `Where` cites file paths in backticks. A path is relative to the repo root.
- `04-before-exposure.md` uses the same table. Its `#` is the order: 1, 2, 3.

## `05-not-done.md`

```markdown
# Not done on purpose

| # | Not done | Why |
| --- | --- | --- |
| 1 | No MFA of its own | The product runs inside a network. An internet-facing instance puts MFA on the proxy. |
```

## `06-claims.md`

Two lists: `## Can claim` and `## Cannot claim`. Each item is one sentence. Under
Cannot claim, name the duties that stay with the operator: the risk assessment,
access reviews, key rotation, backups, and the incident process.

All files are ASCII only.
