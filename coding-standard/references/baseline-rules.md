# Baseline rules

Propose these in step 2 unless the codebase already contradicts them. They are
stack-agnostic. Translate the examples into the project's language.

**File and function size**
- Cap files at **300 lines**; split proactively at **250**. A file that keeps growing is doing too many jobs. Rationale: small files are reviewable, testable, and navigable by humans and agents.
- The split strategy: when a file approaches the cap, extract cohesive pieces into a sibling submodule folder (e.g. `<name>-impl/` with one file per responsibility, or split a fat module into its endpoint/feature units) rather than dumping helpers into a shared `utils`. Keep the public entry point thin and re-export.

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
- Arrange-Act-Assert; one assertion target per case. Mock at the deepest boundary (the data client), not intermediate layers. State what must have a test (e.g. every error condition, every acceptance criterion the card covers).

**Commits**
- Conventional Commits, imperative mood, reference the task/AC id where applicable. Match the project's trailer policy (some forbid co-author trailers).
