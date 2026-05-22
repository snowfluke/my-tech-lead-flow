---
name: technical-spec
description: Produce the technical-specs/ document set (numbered NN-topic.md files plus _index.md) from the groomed business docs, in the Terral/Tatanan format. Grills the user on tech stack and tooling first — this is the architectural keystone the rest of the pipeline depends on — then writes overview, architecture, repo structure, tech stack, module definitions, data model, security, NFRs, auth, integrations, environment config, and ad-hoc trailing specs for areas that need special technical attention. Use when the user wants a technical specification, TSD, architecture/data-model doc, or asks to "write the technical specs".
---

# Technical Specification

This is the architectural keystone of the doc pipeline: it runs **after** the business docs exist (`docs/business/` — user stories, AC, sprint breakdown) and **before** task breakdown, coding standard, and deployment plan, all of which depend on the decisions made here. Get the tech stack and data model right and everything downstream is buildable; get them wrong and every later doc inherits the error.

Output is a **numbered file set** under `docs/technical-specs/`, not one monolith — `_index.md` plus `NN-topic.md` files — so sections are linkable from task cards and reviews (e.g. `technical-specs/06-data-model.md §6.5`).

Two phases: **grill on the architecture, then write the set.**

## Phase 1 — Grill (tech stack and tooling first)

Read the source of truth before asking: all of `docs/business/`, plus any existing `CLAUDE.md`, README, or partial specs. The business docs define *what* is built; this document defines *how*. Then interview the user one question at a time, recommending an answer for each and explaining the trade-off, until every architectural branch is resolved.

**Tech stack and tooling is mandatory and comes first** — it cascades into every other section:

- **Runtime & language** — runtime (Node/Bun/Deno/JVM/Go/Python/…), language + version, strictness.
- **Backend** — framework, API style (REST/GraphQL/RPC), validation/schema layer, ORM/data layer.
- **Frontend** — framework, rendering model (SSR/SPA/SSG), styling, state, forms.
- **Datastores** — primary DB + engine/version, cache, queue, object storage, search. Also nail the **migration and seed mechanism**: the migration tool, and that migrations and seeds run through a programmatic runner that resolves the migrations folder relative to its own module (e.g. `import.meta.dir`/`__dirname`) and takes the connection string from the environment, exposed as stable `db:migrate` / `db:seed` scripts. Forbid hardcoded absolute migration paths and inline raw-SQL file reads; they break inside distroless/minimal images where the operator cannot locate the files.
- **Repository shape** — monorepo vs polyrepo, workspace layout, shared-code package.
- **Tooling** — package manager, type-check / lint / format / test tools, build, CI, e2e.
- **Infra & integrations** — hosting target, containerization, external services/APIs, auth provider.

Then resolve the rest:

- **Architecture** — overall style (monolith/modular-monolith/microservices), module/service boundaries, request flow.
- **Module definitions** — one per bounded area; its responsibility, public surface, and the AC/US it serves.
- **Data model** — every entity, field, type, nullability, default, key, relationship; the ERD; common columns (id/timestamps); state machines for lifecycle entities.
- **Security & auth** — authn mechanism, authz model (roles/RBAC), session/token strategy, secrets, threat surface.
- **NFRs** — volume, throughput, latency, availability targets, scaling assumptions.
- **Integration points** — each external system, its contract, failure mode, and fallback.
- **Environment configuration** — the full env-var set per environment.
- **Operational endpoints** — every project gets two, by default, so deployment and QA have a contract to rely on:
  - A **health-monitor endpoint** (e.g. `GET /health`) that reports liveness and the status of each critical dependency (database, cache, queue, external APIs), so an operator or load balancer can tell at a glance whether the app and its datastores are reachable. Decide the response shape (overall status plus a per-dependency breakdown), whether it is public or guarded, and whether there is a deeper `/health/ready` vs `/health/live` split. This is the redundancy measure that catches a half-broken state, such as the app running but its database wiped or unreachable on a separate VM.
  - A **reset-db-state endpoint** (e.g. `POST /admin/reset-state`) that wipes, re-migrates, and reseeds the database back to a known initial state, choosing the dev seed or the QA seed. This exists so QA can request a reset to initial state without a manual host session. It must be **mounted only in non-production environments (dev / test / SIT / UAT) and absent (not merely access-controlled) in production** — gate it on an environment flag so the route does not exist in prod. Decide the seed-selection input (path, body field, or env), whether it runs synchronously or as a job, and how it is authenticated in the environments where it does exist.

As you go, surface contradictions against the business docs ("AC-10.02 says only Super Admin edits this field, but the data model has no owner/role column — where does that rule live?") and flag decisions that are hard to reverse.

### Identify ad-hoc topics

The Terral/Tatanan format ends with **ad-hoc trailing specs**: a numbered doc per cross-cutting concern that needs focused technical attention and doesn't fit the standard sections — Terral's `12-autocomplete-strategy.md` is the model. During the grill, watch for these: a recurring pattern used across modules, a non-obvious algorithm, a performance-sensitive path, a tricky state machine, a strategy with real alternatives. Propose each candidate to the user and confirm before adding it.

Each ad-hoc doc is the single source of truth for its concern — other docs and task cards **cite it rather than restate it** (open the doc with that instruction). Structure it like `12-autocomplete-strategy.md`:

- A one-paragraph statement of the concern and where it applies, plus a "cite this, don't repeat it" note.
- A **decision matrix** table: `Concern | Decision | Rationale`, one row per resolved choice (the heart of the doc).
- The **interface / request shape** — the exact API call, function signature, or data contract, in a code block.
- A **performance targets** table with a source for each number (cross-referencing the NFR doc).
- Any rate-limit / security constraints specific to this concern.
- The **component/contract** it produces (file layout + the locked public type signature).
- A **"What this does NOT do"** section — explicit non-goals, each saying why and where the responsibility actually lives.
- A **cross-references** table mapping each related concern to its source doc/card.
- An **open follow-ups** list — deferred-but-flagged decisions, each with the trigger condition for revisiting.

When every branch is resolved, summarize the stack and the planned file list, and confirm before writing.

## Phase 2 — Write the set

Write to `docs/technical-specs/`. Standard core, in order, each as `NN-topic.md`:

1. Overview — open with a prose intro, then a **Terminology** callout (point at the glossary) and, for multilingual projects, a **Language policy** callout (which language is UI copy, which is code/identifiers). Then goals, scope-by-module (a subsection per module listing in-scope items with their AC/US, plus an explicit **Out of Scope** subsection), user base, a **business-workflow summary as pseudocode** (the real flow per role, like the SPK example), and a **numbered Assumptions & Known Constraints** list.
2. System Architecture — the style and why ("Why This Shape" rationale), plus **Mermaid diagrams**: a high-level component graph, a request-lifecycle sequence diagram, and a deployment graph. Close with a service/module **boundary map** table and the rule for cross-module calls (modules don't import each other's internals).
3. Repository Structure — the directory tree with a per-folder purpose annotation.
4. Tech Stack — **dense tables grouped by concern** (runtime/language, backend, frontend, datastores, security, testing/CI, deployment, storage), each row `Component | Technology | Justification`. Pin versions. Add a **"What we deliberately do NOT use"** table (tool → reason) and a version-pinning policy. Every choice is one the user confirmed in the grill.
5. Module Definitions — one numbered subsection per module: responsibility, public surface/API, the entities it owns, and the AC/US it serves. Note shared-package usage and the no-cross-internal-import rule. Include the **operational endpoints** (health monitor and, where mounted, reset-db-state) in whichever module owns them: document the route, method, request/response shape, the per-dependency health breakdown, the dev/QA seed-selection input, and the environment gating that keeps reset-state out of production.
6. Data Model — an ERD (Mermaid `erDiagram` or equivalent), then table definitions with `column | type | nullable | default | key | notes` and **example values**, common-column conventions (id/timestamps), and **state machines** for lifecycle entities. Mirror the glossary: `### CUSTOMERS (UI label: "Pelanggan")`. Close with a **Migrations and seeding** subsection that locks the mechanism: a programmatic runner whose migrations folder is resolved relative to its module and whose connection string comes from the environment, surfaced as `db:migrate` / `db:seed` commands. Show the runner shape and state the rule explicitly. Do this:

   ```ts
   import { migrate } from "drizzle-orm/bun-sql/migrator";
   import { db, sql } from "./client";
   import { join } from "path";

   await migrate(db, { migrationsFolder: join(import.meta.dir, "migrations") });
   await sql.close();
   ```

   Not a hardcoded path with an inlined connection string and a raw `unsafe()` read of one `.sql` file; that applies schema outside the migration ledger and cannot find its files in a distroless image. The dev seed and QA seed are separate, idempotent, version-controlled scripts selected by the reset-db-state endpoint.
7. Security — authn/authz, rate limiting, CORS, CSP, request hardening, object-store access; table per concern with the implementation. Document the **operational-endpoint policy** here: the health endpoint's exposure (public vs guarded), and the reset-db-state endpoint's hard rule — mounted only in dev / test / SIT / UAT, conditionally registered behind an environment flag so the route does not exist in production, with a note that this is enforced at route registration, not just by authorization.
8. Non-Functional Requirements — concrete numbers (volume, latency budgets, throughput, availability), each with a source; these become the targets later sections and ad-hoc docs reference.
9. Authentication and Authorization — mechanism, token/session strategy, the role matrix.
10. Integration Points — each external system: contract, failure mode, fallback, cache/invalidation rules.
11. Environment Configuration — the full env-var set, annotated, per environment. Include the flag that gates the reset-db-state endpoint (e.g. `ENABLE_RESET_API` / `APP_ENV`) and the seed-selection variable, with their values per environment shown explicitly as off/absent in production.

Then the **ad-hoc trailing docs** (12, 13, …), one per confirmed special-attention topic.

Finally `_index.md`: the version/date/author/status/phase header, a numbered Table of Contents linking every file, and a **Companion Documents** table linking the sibling docs (`../business/`, `../GLOSSARY.md`, `../CODING_STANDARD.md`, `../TASK_BREAKDOWN.md`, `../DEPLOYMENT_PLAN.md`, `../api-specs/`, etc.) — link them even if they don't exist yet, since they're produced later in the pipeline.

### Writing rules

- Number sections within each file (`## 6.1`, `### 6.2`) so they're citable as stable anchors.
- Trace every module and data-model decision back to the AC/US it serves; this is a spec *of the business docs*, not free invention. Where the business docs are silent, raise it during the grill rather than guessing.
- Preserve domain terms and non-English UI labels verbatim; mirror the glossary (`### CUSTOMERS (UI label: "Pelanggan")`).
- Keep `_index.md` and the file numbering consistent; if you add or reorder files, update the TOC.
- If a technical-specs set already exists, read it and update affected files in place rather than clobbering; report what changed.
### Helper script

After writing or reordering files, verify `_index.md` still matches the file set:

```bash
python scripts/check_index.py --specs-dir docs/technical-specs
```

It reports entries linked in the index but missing on disk, files on disk not
linked from the index, and gaps in the `NN` numbering. Exit is non-zero on any
mismatch.

### Writing conventions

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- Metadata header lines (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`) each end with two trailing spaces so Markdown renders them on separate lines.
