---
name: api-spec
description: Produce the api-specs/ document set (numbered NN-topic.md files plus _index.md) from the technical specs, in the Terral/Tatanan format. Derives every operation, its inputs/outputs, errors, and access rules from the module definitions and data model already decided in docs/technical-specs/, and writes them in whatever protocol the project chose — REST, GraphQL, gRPC, or SOAP. Use when the user wants an API specification, endpoint contracts, an OpenAPI/schema/proto/WSDL companion, or asks to "write the api specs". Runs after technical-spec and before task-breakdown.
---

# API Specification

The interface contract for the system. It runs **after** `technical-spec` (the architecture, modules, and data model must already exist in `docs/technical-specs/`) and **before** `task-breakdown`, `tech-lead-setups`, and `code-review`, all of which cite endpoint contracts. The technical specs decide *what modules exist and what data they own*; this set pins down *the exact wire contract a client calls and a server must honor*.

Output is a **numbered file set** under `docs/api-specs/`, not one monolith — `_index.md` plus `NN-topic.md` files — so a single resource or operation is linkable from task cards, stubs, and reviews (e.g. `api-specs/03-work-orders.md` → `POST /work-orders`).

The protocol is **already decided** in `technical-specs/04-tech-stack.md` (API style: REST / GraphQL / gRPC / SOAP). Do not re-litigate it; read it, confirm it, and write the contract in that protocol's idiom. The document set's job is identical across protocols (`<protocol-agnostic-core>`); only the surface notation changes (`<protocol-idioms>`).

Two phases: **derive the surface from the technical specs, then write the set.**

## Phase 1 — Derive the surface

Read the source of truth before writing anything. The api-specs are a *projection* of the technical specs, not new invention:

- `technical-specs/04-tech-stack.md` — the **API style/protocol** and the validation/schema layer. This selects the idiom for the whole set.
- `technical-specs/05-module-definitions.md` — the public surface of each module. Each module becomes one `NN-<resource>.md` file; its listed operations become the documented operations.
- `technical-specs/06-data-model.md` — every entity, field, type, nullability, default, and state machine. Request/response shapes, enums, and valid transitions come straight from here. Do not invent fields the data model does not have.
- `technical-specs/07-security.md` and `09-authentication-and-authorization.md` — the authn mechanism and the role matrix. These become the per-operation **Access** line and the auth conventions file.
- `technical-specs/11-environment-configuration.md` and the operational endpoints (health monitor, reset-db-state) — these become the `system` resource file, with the production gating noted.
- `docs/business/` — the AC/US each operation serves. Every operation cites the AC/US that justifies it; an operation tracing to no AC/US is a flag to raise, not a row to write.

Confirm the protocol and the planned file list (one per module plus conventions, authentication, system, and the index) with the user before writing. Surface contradictions against the technical specs as you go ("module-definitions §5.8 says only Super Admin sets this field, but the data model has no role column on it — where is that enforced?"). Only grill where the technical specs are genuinely silent on a contract detail (e.g. pagination defaults, idempotency keys, an envelope shape the specs never pinned); recommend a default for each and confirm.

## Phase 2 — Write the set

Write to `docs/api-specs/`. The file set, in order:

1. **`01-conventions.md`** — the transport contract shared by every operation, in the project's protocol idiom (`<protocol-idioms>`): base address, message/content type, the success and error envelope, pagination, the full status/fault-code table, standard error codes mapped to their condition, and a **role reference** table mirroring the auth doc. This is the single source for cross-cutting rules; every resource file cites it rather than restating.
2. **`02-authentication.md`** — the login / refresh / logout (or token-issue) operations, fully documented including the token/cookie strategy from the technical specs.
3. **`NN-<resource>.md`** — one file per module/bounded resource from `05-module-definitions.md`. Each operation documented per `<protocol-agnostic-core>`. Order resources by dependency (foundational/master data and the entities others reference first).
4. **`system.md`** (last numbered resource) — the operational endpoints: health monitor (aggregate and per-dependency) and, where mounted, reset-db-state, with the rule that it is registered only in non-production environments.
5. **`_index.md`** — the version/base-address header, an **Operation Status Tracker** grouped by resource (legend: `OK` implemented and tested, `WIP` in progress, `TODO` not started, `SCAFFOLD` Tech Lead stub returning a mock), a **Files in This Directory** table, and a **Companion Documents** link back to `../technical-specs/` and `../business/`. The tracker is the at-a-glance build state the task board and stubs sync against.

If an api-specs set already exists, read it and update affected files in place rather than clobbering; report what changed and keep `_index.md` consistent with the files on disk.

<protocol-agnostic-core>

Whatever the protocol, **every operation** documents the same eight things. Only the notation differs.

1. **Signature** — the operation's address in the protocol's idiom (REST method + path, GraphQL field on Query/Mutation/Subscription, gRPC `service.Method`, SOAP operation name).
2. **Purpose** — one line: what it does and the user action or workflow step that triggers it.
3. **Access** — which roles may call it, citing the role matrix. Note field- or status-scoped permissions.
4. **Input** — the request shape with a field table: `field | type | required | notes`. Mark which fields are conditional and on what. Types and enums come from the data model.
5. **Behavior** — the server-side steps in order: validation, lookups, state transitions, side effects. Cite the AC/US driving each rule.
6. **Output** — the success response shape with an example, and the status/result it returns. Note nullable fields and what the client renders for them.
7. **Errors / faults** — a table of every failure: `code | status | condition`. Pull from the standard error codes in conventions; add operation-specific ones.
8. **Traceability** — the AC/US IDs the operation satisfies, inline where each rule appears.

This core is the spec. A REST endpoint, a GraphQL mutation, a gRPC method, and a SOAP operation that all do the same job carry the same eight facts; the reviewer and the implementer read the same contract regardless of wire format.

</protocol-agnostic-core>

<protocol-idioms>

Read the chosen protocol from `technical-specs/04-tech-stack.md` and write `01-conventions.md` and every operation in its idiom. The Terral and Tatanan example sets are **REST**; use them as the shape for REST and translate the same structure for the others.

**REST** (the example projects' style)
- Conventions: base URL (`/api/v1`), `application/json` (+ `multipart/form-data` for uploads), `Authorization: Bearer` header, success/collection/error envelope, pagination params (`page`/`limit`/`sort`/`order`), HTTP status code table, standard error-code table.
- Signature: `METHOD /path/:param`. Inputs split into path params, query params, and body. Output keyed by HTTP status (200/201/204…). Errors map a code to an HTTP status.

**GraphQL**
- Conventions: the single endpoint (`POST /graphql`), the SDL type conventions, scalar choices, the error `extensions.code` convention (GraphQL returns 200 with an `errors` array, not HTTP status codes — say so explicitly), pagination via Relay connections (`edges`/`pageInfo`) or offset, and persisted-query/depth-limit rules if any.
- Signature: a field on `Query`, `Mutation`, or `Subscription`, shown as an SDL snippet with its argument and return types. Inputs are the field arguments / `input` types. Output is the return type. Errors are `extensions.code` values, each mapped to a condition.

**gRPC**
- Conventions: the proto package and version, the canonical `google.rpc.Status` / status-code table, metadata (auth token in metadata, not a header), deadline/timeout policy, and streaming conventions (unary vs server/client/bidi).
- Signature: `package.Service/Method` with its request and response message names, shown as a `.proto` snippet. Inputs/outputs are the protobuf messages with field numbers. Errors are gRPC status codes plus error-detail messages.

**SOAP**
- Conventions: the WSDL location, the SOAP envelope and target namespaces, the binding style (document/literal), the fault structure (`faultcode`/`faultstring`/`detail`), and any WS-Security header.
- Signature: the operation name and its request/response message elements, shown as the XML element shapes. Inputs/outputs are the XSD-typed elements. Errors are SOAP faults, each mapped to a condition.

When the protocol is something else, keep the eight-part core and write the conventions and signatures in that protocol's native notation. The contract is what matters; the syntax serves it.

</protocol-idioms>

## Writing rules

- The api-specs are a projection of the technical specs. Trace every operation to a module and every field to the data model; where the specs are silent, raise it in Phase 1 rather than inventing the contract.
- Cite, do not restate: cross-link `../technical-specs/` sections (`[../technical-specs/06-data-model.md §6.5](...)`) for authoritative field rules, role matrices, and state machines instead of duplicating them.
- Preserve domain terms and non-English UI labels and messages verbatim; mirror the glossary. If error messages are user-facing in a non-English UI language, keep `code` in English and the `message` in the UI language, as the example sets do.
- Keep `_index.md`, the operation status tracker, and the file numbering consistent; if you add or reorder files, update the index and tracker.
- Number sections within each file so operations are citable as stable anchors.

## Writing conventions

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- Metadata header lines (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`) each end with two trailing spaces so Markdown renders them on separate lines.
</content>
