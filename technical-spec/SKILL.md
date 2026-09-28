---
name: technical-spec
description: Produce the technical-specs/ document set (numbered NN-topic.md files plus _index.md) from the groomed business docs. Grills the user on tech stack and tooling first (this is the architectural keystone the rest of the pipeline depends on), then writes overview, architecture, repo structure, tech stack, module definitions, data model, security, NFRs, auth, integrations, environment config, and ad-hoc trailing specs for areas that need special technical attention. Use when the user wants a technical specification, TSD, architecture/data-model doc, or asks to "write the technical specs".
---

# Technical Specification

This is the architectural keystone of the doc pipeline: it runs **after** the business docs exist (`docs/business/`: user stories, AC, sprint breakdown) and **before** the API specs, task breakdown, coding standard, and deployment plan, all of which depend on the decisions made here. Get the tech stack and data model right and everything downstream is buildable; get them wrong and every later doc inherits the error.

When this set is written and confirmed, the next step is `api-spec`, which projects the module definitions and data model into the `docs/api-specs/` endpoint contracts in whatever protocol the tech stack chose.

Output is a **numbered file set** under `docs/technical-specs/`, not one monolith (`_index.md` plus `NN-topic.md` files), so sections are linkable from task cards and reviews (e.g. `technical-specs/06-data-model.md` section 6.5).

Two phases: **grill on the architecture, then write the set.**

**Running project (adopt mode).** If the repository already has working code, describe the system as built. Read the code, the config, the schema or migrations, and the deploy files, and write each section from what exists. The grill confirms what you read; it does not redesign. Record every gap or inconsistency you find (no rate limit, two auth paths, a table with no owner module) in a **Findings** list at the end of the section it belongs to, and repeat the list in your report. `docs/business/` may not exist; then leave out the AC and US traceability, and say so in `_index.md`.

## Phase 1: Grill (tech stack and tooling first)

Read the source of truth before asking: all of `docs/business/`, plus any existing `CLAUDE.md` or `AGENTS.md`, README, or partial specs. The business docs define *what* is built; this document defines *how*. Then interview the user one question at a time, recommending an answer for each and explaining the trade-off, until every architectural branch is resolved.

This is a genuine grill, not a form. Hold the discipline:

- **One decision per turn.** Do not paste the bullet lists below at the user as a questionnaire to fill in. Ask the live question, give your recommended answer and the one reason it wins over the runner-up, and wait. The lists are *your* checklist of what must be closed, not the user's intake form.
- **Walk the branch the answer opens.** Each answer changes what to ask next (picking microservices opens service boundaries, transport, and data ownership; picking a modular monolith does not). Follow the branch the user's choice creates before starting a new one; don't return to a flat list.
- **Confirm before moving on.** Restate the decision in one line and get explicit agreement before leaving it, especially for the hard-to-reverse ones (architecture style, module boundaries, primary datastore).

**Tech stack and tooling is mandatory and comes first**; it cascades into every other section:

- **Runtime & language**: runtime (Node, Bun, Deno, JVM, Go, Python, and so on), language + version, strictness.
- **Backend**: framework, API style (REST/GraphQL/RPC), validation/schema layer, ORM/data layer.
- **Frontend**: framework, rendering model (SSR/SPA/SSG), styling, state, forms.
- **Datastores**: primary DB + engine/version, cache, queue, object storage, search. Also nail the **migration and seed mechanism**: one stable migrate command and one seed command, per the rule in [references/layout.md](references/layout.md) (item 6, Data Model).
- **Repository shape**: monorepo vs polyrepo, workspace layout, shared-code package.
- **Tooling**: package manager, type-check / lint / format / test tools, build, CI, e2e.
- **Infra & integrations**: hosting target, containerization, external services/APIs, auth provider.

Then resolve the rest. **Architecture style and module boundaries are the hardest to reverse: grill them hardest.** Don't accept the first style the user names: lay out the realistic options against *this* project's NFRs and team size, give a recommendation with the trade-off, and get explicit buy-in before treating it as decided. Then derive module boundaries from the bounded areas in the business docs one at a time, confirming each owns a coherent slice before naming the next.

**Design each module to be deep**, with the lens in [references/module-design.md](references/module-design.md#vocabulary):

- A module is **deep** when a lot of behaviour sits behind a small **interface**, and "interface" means everything a caller must know (invariants, error modes, ordering, config), not just the signatures. Push back on shallow modules whose interface is nearly as wide as their implementation; that is usually a sign two modules should merge or one should absorb a pass-through.
- Apply the **deletion test** to every proposed boundary: imagine deleting the module. If the complexity just moves to its callers, the boundary earns its keep; if complexity vanishes, it was a pass-through and the boundary is wrong.
- Classify every cross-module or cross-service dependency by the categories in [references/module-design.md](references/module-design.md#dependency-categories) (in-process, local stand-in, remote owned, remote third party). Where the answer is remote owned or remote third party, define a **port** at the seam and inject the transport as an **adapter**, so the logic stays in one deep module testable behind an in-memory adapter. Only introduce a port where two adapters are actually justified (production plus test); a single-adapter seam is just indirection.
- For the one or two riskiest module interfaces (the ones most callers depend on, or hardest to change later), offer the **Design it twice** exploration in [references/module-design.md](references/module-design.md#design-it-twice): draft several different interfaces, compare by depth and seam placement, and let the user pick before the shape is locked into the spec.

- **Architecture**: overall style (monolith/modular-monolith/microservices), module/service boundaries, request flow.
- **Module definitions**: one per bounded area; its responsibility, public surface, and the AC/US it serves.
- **Data model**: every entity, field, type, nullability, default, key, relationship; the ERD; common columns (id/timestamps); state machines for lifecycle entities.
- **Security & auth**: authn mechanism, authz model (roles/RBAC), session/token strategy, secrets, and each trust boundary with its threats and controls.
- **NFRs**: volume, throughput, latency, availability targets, scaling assumptions.
- **Integration points**: each external system, its contract, failure mode, and fallback.
- **Environment configuration**: the full env-var set per environment.
- **Operational endpoints**: every project gets two, by default, so deployment and QA have a contract to rely on:
  - A **health-monitor endpoint** (e.g. `GET /health`) that reports liveness and the status of each critical dependency (database, cache, queue, external APIs), so an operator or load balancer can tell at a glance whether the app and its datastores are reachable. Decide the response shape (overall status plus a per-dependency breakdown), whether it is public or guarded, and whether there is a deeper `/health/ready` vs `/health/live` split. This is the redundancy measure that catches a half-broken state, such as the app running but its database wiped or unreachable on a separate VM.
  - A **reset-db-state endpoint** (e.g. `POST /admin/reset-state`) that wipes, re-migrates, and reseeds the database back to a known initial state, choosing the dev seed or the QA seed. This exists so QA can request a reset to initial state without a manual host session. It must be **mounted only in non-production environments (dev / test / SIT / UAT) and absent (not merely access-controlled) in production**: gate it on an environment flag so the route does not exist in prod. Decide the seed-selection input (path, body field, or env), whether it runs synchronously or as a job, and how it is authenticated in the environments where it does exist.

As you go, surface contradictions against the business docs ("AC-10.02 says only Super Admin edits this field, but the data model has no owner/role column; where does that rule live?") and flag decisions that are hard to reverse.

### Identify ad-hoc topics

The set ends with **ad-hoc trailing specs**: a numbered doc per cross-cutting concern that needs focused technical attention and doesn't fit the standard sections, for example `12-search-strategy.md` for a search feature with real design alternatives. During the grill, watch for these: a recurring pattern used across modules, a non-obvious algorithm, a performance-sensitive path, a tricky state machine, a strategy with real alternatives. Propose each candidate to the user and confirm before adding it.

Each ad-hoc doc is the single source of truth for its concern: other docs and task cards **cite it rather than restate it** (open the doc with that instruction). Structure it like `12-autocomplete-strategy.md`:

- A one-paragraph statement of the concern and where it applies, plus a "cite this, don't repeat it" note.
- A **decision matrix** table: `Concern | Decision | Rationale`, one row per resolved choice (the heart of the doc).
- The **interface / request shape**: the exact API call, function signature, or data contract, in a code block.
- A **performance targets** table with a source for each number (cross-referencing the NFR doc).
- Any rate-limit / security constraints specific to this concern.
- The **component/contract** it produces (file layout + the locked public type signature).
- A **"What this does NOT do"** section: explicit non-goals, each saying why and where the responsibility actually lives.
- A **cross-references** table mapping each related concern to its source doc/card.
- An **open follow-ups** list: deferred-but-flagged decisions, each with the trigger condition for revisiting.

When every branch is resolved, summarize the stack and the planned file list, and confirm before writing.

## Phase 2: Write the set

Write to `docs/technical-specs/` in the layout of [references/layout.md](references/layout.md): the standard core files in order, then one ad-hoc trailing doc per confirmed special-attention topic, then `_index.md`.

### Writing rules

- Number sections within each file (`## 6.1`, `### 6.2`) so they're citable as stable anchors.
- Trace every module and data-model decision back to the AC/US it serves; this is a spec *of the business docs*, not free invention. Where the business docs are silent, raise it during the grill rather than guessing.
- Preserve domain terms and non-English UI labels verbatim; mirror the glossary (`### CUSTOMERS (UI label: "Pelanggan")`).
- Keep `_index.md` and the file numbering consistent; if you add or reorder files, update the TOC.
- If a technical-specs set already exists, read it and update affected files in place rather than clobbering; report what changed.
### Helper script

After writing or reordering files, verify `_index.md` still matches the file set:

```bash
python3 <this skill's dir>/scripts/check_index.py --specs-dir docs/technical-specs
```

It reports entries linked in the index but missing on disk, files on disk not
linked from the index, and gaps in the `NN` numbering. Exit is non-zero on any
mismatch.

### Writing conventions

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- Metadata header lines (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`) each end with two trailing spaces so Markdown renders them on separate lines.
