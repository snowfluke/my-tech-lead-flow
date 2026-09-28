# Baseline rules

Propose these in step 2 unless the codebase already contradicts them. They are
stack-agnostic. Translate the examples into the project's language.

**File and function size**
- Cap files at **300 lines**; split proactively at **250**. A file that keeps growing is doing too many jobs. Rationale: small files are reviewable, testable, and navigable by humans and agents.
- The split strategy: when a file approaches the cap, extract cohesive pieces into a sibling submodule folder (e.g. `<name>-impl/` with one file per responsibility, or split a fat module into its endpoint/feature units) rather than dumping helpers into a shared `utils`. Keep the public entry point thin and re-export.

**Complexity**
- Every function stays at cyclomatic complexity 10 or under **(enforced)**. Split an over-limit function by extracting a named function. Never suppress the rule. Rationale: a function with more than ten paths cannot be covered by a few tests.

**Tooling** (enforced by the linter, the formatter, and the hooks)

| Ecosystem | Lint | Format | Complexity rule |
| --- | --- | --- | --- |
| JS/TS | oxlint with the [anti-slop](https://github.com/dmmulroy/anti-slop) plugin | oxfmt | oxlint `complexity: ["error", { "max": 10 }]` |
| Go | golangci-lint | gofmt | the `cyclop` or `gocyclo` linter |
| Python | ruff | ruff format | ruff `C901` |
| Rust | clippy | rustfmt | clippy `cognitive_complexity` |

- Pre-commit hooks run the format check, the linter, and the type-checker on staged files. The aggregate check command runs before hand-off and in CI.
- Mark every rule a tool enforces as **(enforced)** and state the tool, so review time goes to what tools cannot catch.

**Type safety** (typed languages)
- No untyped escape hatches: no `any`, no unchecked casts (`as`), no non-null assertions (`!`). Use real narrowing and handle null/undefined explicitly. Rationale: each escape hatch is a place the type system stops protecting you.
- Explicit return types on exported functions. Prefer literal unions over loose enums where the language allows.
- Derive types from the validation schema (one source of truth) rather than declaring them twice.

**Layering**
- No business logic in route/handler/controller code; it belongs in a service layer.
- No direct data-store access outside a repository/data layer.
- Modules do not import each other's internals; cross-cutting needs go through a shared helper. Rationale: boundaries are what make a module extractable and testable later.

**Correctness hygiene**
- No magic numbers or strings; name them as constants.
- No dead code, no commented-out code; delete it (version control remembers).
- Domain errors over raw throws; map them to the response envelope at the boundary. Never swallow an error into a bare log.
- Every multi-step write that must be atomic runs in a transaction; audit/side-effect writes share that transaction.

**No partial work in shipped code**
- No `// TODO` / `// FIXME` in merged code, except one explicitly sanctioned deferral pattern (e.g. a documented deferred-dependency marker) that the PR description lists. Rationale: a standard that tolerates open TODOs tolerates half-finished features.

**Configuration and secrets**
- No raw environment access scattered through the code; read config through one validated module. No secrets in the repo.

**Tests**
- Every test names one behaviour and fails when that behaviour breaks. Before a test is committed, break the implementation once (invert a condition, delete the branch) and watch the test fail.
- No tautological tests: no expected value produced by the code under test, no mock of the unit under test, no assertion inside a branch that may not run, no test that survives deleting the implementation body.
- No change-detector tests: no re-recorded snapshots, no assertions on internal calls or private structure. A test that fails while the behaviour is unchanged is rewritten or deleted.
- Arrange-Act-Assert. Mock only at the system edge (network, clock, third-party service), never the unit under test or the project's own modules.
- For a complex feature, the e2e tests cover realistic scenarios of medium or high complexity: several steps, real data shapes, and a failure or permission path. The simplest success case alone is not enough.
- For a bug fix, first check whether an existing behaviour test should have caught the bug. If so, fix that test. Add a new regression test only when no behaviour test covers the case.
- State what must have a test: every error condition the service owns, and every acceptance criterion the card covers.
- Local e2e runs stay light: capped workers, one headless browser, the running dev server reused, only the affected specs, heavy scenarios tagged and left to CI, traces and video only on failure. The suite stops every process it started.

**Commits, branches, and pull requests**
- Conventional Commits, imperative mood, the card ID in the subject or body.
- Branch names carry the card: `<type>/<card-id>-<slug>`, for example `feat/BE-S2-05-csv-export`. Work from an issue with no card uses the issue number: `fix/123-login-timeout`.
- ASCII only in commit messages, PR titles, and PR bodies: no em or en dashes, no emoji, no arrows. Use `-`, `:`, and `->`. Source files may hold any language.
- No attribution: no `Co-Authored-By` trailer, no "Generated with" line.
- The PR body fills every section of the PR template.
- A `BE` or `FE` card's PR changes a test. A wiring card's PR changes an e2e test. A `fix` or `feat` issue's PR changes a test. A `TL` or `DB` chore may change none.
- A test that proves an AC names the AC ID in its title. Every AC ID in a PR body appears in a changed test.
- A PR is done when it opens. No to-do tags, skipped tests, or focused tests in the diff. Left-over work gets its own card or issue, and the PR names it.
- Language policy: code, commit messages, and PR text in English. UI copy and domain terms in the language of the business docs, verbatim.

These rules are enforced **(enforced)**. `10-comments-commits-and-docs.md` carries them in this block, which the hooks and CI read. Adjust the values to the project; keep every key.

```pr-hygiene
branch: ^(feat|fix|chore|docs|refactor|test)/(?P<kind>BE|FE|TL|DB)-S\d+-\d+-[a-z0-9-]+$
branch: ^(?P<kind>feat|fix|chore|docs|refactor|test)/\d+-[a-z0-9-]+$
commit-subject: ^(feat|fix|chore|docs|refactor|test|perf)(\([a-z0-9-]+\))?: \S.{0,70}$
forbidden: Co-Authored-By
forbidden: Generated with
forbidden: Generated by
pr-heading: ## Summary
pr-heading: ## Card
pr-heading: ## Tests
pr-heading: ## Checklist
test-files: (\.test\.|\.spec\.|/tests?/)
e2e-files: ^e2e/
tests-required: BE FE feat fix
ac-id: \bAC-\d+(?:\.\d+)*\b
```
