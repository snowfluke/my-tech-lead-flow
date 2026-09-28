# Technical specs layout

The files `SKILL.md` Phase 2 writes to `docs/technical-specs/`. Other skills link
to these file names (`03-repository-structure.md`, `04-tech-stack.md`,
`05-module-definitions.md`, `07-security.md`, `11-environment-configuration.md`),
so keep the numbers.

## Standard core

In order, each as `NN-topic.md`:

1. Overview: open with a prose intro, then a **Terminology** callout (point at the glossary) and, for multilingual projects, a **Language policy** callout (which language is UI copy, which is code/identifiers). Then goals, scope-by-module (a subsection per module listing in-scope items with their AC/US, plus an explicit **Out of Scope** subsection), user base, a **business-workflow summary as pseudocode** (the real flow per role, like the SPK example), and a **numbered Assumptions & Known Constraints** list.
2. System Architecture: the style and why ("Why This Shape" rationale), plus **Mermaid diagrams**: a high-level component graph, a request-lifecycle sequence diagram, and a deployment graph. Close with a service/module **boundary map** table and the rule for cross-module calls (modules don't import each other's internals).
3. Repository Structure: the directory tree with a per-folder purpose annotation.
4. Tech Stack: **dense tables grouped by concern** (runtime/language, backend, frontend, datastores, security, testing/CI, deployment, storage), each row `Component | Technology | Justification`. Pin versions. Add a **"What we deliberately do NOT use"** table (tool -> reason) and a version-pinning policy. Every choice is one the user confirmed in the grill.
5. Module Definitions: one numbered subsection per module, with its responsibility, public surface/API, the entities it owns, and the AC/US it serves. Write the public surface as the module's full **interface** (invariants, error modes, ordering, config), not just method signatures, and name the **seam** where each external dependency is injected and which adapters sit there (production vs test). State why the module is deep: the behaviour it hides behind that surface. Note shared-package usage and the no-cross-internal-import rule. Include the **operational endpoints** (health monitor and, where mounted, reset-db-state) in whichever module owns them: document the route, method, request/response shape, the per-dependency health breakdown, the dev/QA seed-selection input, and the environment gating that keeps reset-state out of production.
6. Data Model: an ERD (Mermaid `erDiagram` or equivalent), then table definitions with `column | type | nullable | default | key | notes` and **example values**, common-column conventions (id/timestamps), and **state machines** for lifecycle entities. Mirror the glossary: `### CUSTOMERS (UI label: "Pelanggan")`. Close with a **Migrations and seeding** subsection that locks the mechanism for whatever stack the project chose: a runner whose migrations location is resolved relative to its own module/package and whose connection string comes from the environment, surfaced as a stable migrate/seed command. State the rule, then show it in the project's actual language. The TypeScript/Bun shape, as one example:

   ```ts
   import { migrate } from "drizzle-orm/bun-sql/migrator";
   import { db, sql } from "./client";
   import { join } from "path";

   // migrations folder resolved relative to this module, not an absolute path
   await migrate(db, { migrationsFolder: join(import.meta.dir, "migrations") });
   await sql.close();
   ```

   Forbid the inverse in any language: a hardcoded absolute path with an inlined connection string and a raw read/exec of one `.sql` file; that applies schema outside the migration ledger and cannot find its files in a distroless image. The dev seed and QA seed are separate, idempotent, version-controlled scripts selected by the reset-db-state endpoint.
7. Security: start with a **threat model**: one row per trust boundary (browser to API, API to database, API to each third party, admin surface), with the threats that cross it and the control that stops each one. Then authn/authz, rate limiting, CORS, CSP, request hardening, object-store access; table per concern with the implementation. Give every control a short ID (`SEC-01`, `SEC-02`, ...). `coding-standard` turns each control into one review checklist item, so a control without an ID is never checked. Document the **operational-endpoint policy** here: the health endpoint's exposure (public vs guarded), and the reset-db-state endpoint's hard rule: mounted only in dev / test / SIT / UAT, conditionally registered behind an environment flag so the route does not exist in production, with a note that this is enforced at route registration, not just by authorization.
8. Non-Functional Requirements: concrete numbers (volume, latency budgets, throughput, availability), each with a source; these become the targets later sections and ad-hoc docs reference.
9. Authentication and Authorization: mechanism, token/session strategy, the role matrix.
10. Integration Points: each external system with its contract, failure mode, fallback, cache/invalidation rules.
11. Environment Configuration: the full env-var set, annotated, per environment. Include the flag that gates the reset-db-state endpoint (e.g. `ENABLE_RESET_API` / `APP_ENV`) and the seed-selection variable, with their values per environment shown explicitly as off/absent in production.

## Ad-hoc trailing docs

Files 12, 13, and on, one per confirmed special-attention topic.

## `_index.md`

`_index.md` holds the version/date/author/status/phase header, a numbered Table of Contents linking every file, and a **Companion Documents** table linking the sibling docs (`../business/`, `../GLOSSARY.md`, `../coding-standard/`, `../task-breakdown/`, `../deployment-plan/`, `../api-specs/`, etc.): link them even if they don't exist yet, since they're produced later in the pipeline.
