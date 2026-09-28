# Contract format

`SKILL.md` Phase 2 links here.

## Protocol-agnostic core

Every operation, in any protocol, documents these parts.

Whatever the protocol, **every operation** documents the same eight things. Only the notation differs.

1. **Signature**: the operation's address in the protocol's idiom (REST method + path, GraphQL field on Query/Mutation/Subscription, gRPC `service.Method`, SOAP operation name).
2. **Purpose**: one line on what it does and the user action or workflow step that triggers it.
3. **Access**: which roles may call it, citing the role matrix. Note field- or status-scoped permissions.
4. **Input**: the request shape with a field table (`field | type | required | notes`). Mark which fields are conditional and on what. Types and enums come from the data model.
5. **Behavior**: the server-side steps in order (validation, lookups, state transitions, side effects). Cite the AC/US driving each rule.
6. **Output**: the success response shape with an example, and the status/result it returns. Note nullable fields and what the client renders for them.
7. **Errors / faults**: a table of every failure (`code | status | condition`). Pull from the standard error codes in conventions; add operation-specific ones.
8. **Traceability**: the AC/US IDs the operation satisfies, inline where each rule appears.

This core is the spec. A REST endpoint, a GraphQL mutation, a gRPC method, and a SOAP operation that all do the same job carry the same eight facts; the reviewer and the implementer read the same contract regardless of wire format.

## Protocol idioms

How each protocol expresses the core.

Read the chosen protocol from `technical-specs/04-tech-stack.md` and write `01-conventions.md` and every operation in its idiom. The example and example example sets are **REST**; use them as the shape for REST and translate the same structure for the others.

**REST** (the example projects' style)
- Conventions: base URL (`/api/v1`), `application/json` (+ `multipart/form-data` for uploads), `Authorization: Bearer` header, success/collection/error envelope, pagination params (`page`/`limit`/`sort`/`order`), HTTP status code table, standard error-code table.
- Signature: `METHOD /path/:param`. Inputs split into path params, query params, and body. Output keyed by HTTP status (200/201/204…). Errors map a code to an HTTP status.

**GraphQL**
- Conventions: the single endpoint (`POST /graphql`), the SDL type conventions, scalar choices, the error `extensions.code` convention (GraphQL returns 200 with an `errors` array, not HTTP status codes; say so explicitly), pagination via Relay connections (`edges`/`pageInfo`) or offset, and persisted-query/depth-limit rules if any.
- Signature: a field on `Query`, `Mutation`, or `Subscription`, shown as an SDL snippet with its argument and return types. Inputs are the field arguments / `input` types. Output is the return type. Errors are `extensions.code` values, each mapped to a condition.

**gRPC**
- Conventions: the proto package and version, the canonical `google.rpc.Status` / status-code table, metadata (auth token in metadata, not a header), deadline/timeout policy, and streaming conventions (unary vs server/client/bidi).
- Signature: `package.Service/Method` with its request and response message names, shown as a `.proto` snippet. Inputs/outputs are the protobuf messages with field numbers. Errors are gRPC status codes plus error-detail messages.

**SOAP**
- Conventions: the WSDL location, the SOAP envelope and target namespaces, the binding style (document/literal), the fault structure (`faultcode`/`faultstring`/`detail`), and any WS-Security header.
- Signature: the operation name and its request/response message elements, shown as the XML element shapes. Inputs/outputs are the XSD-typed elements. Errors are SOAP faults, each mapped to a condition.

When the protocol is something else, keep the eight-part core and write the conventions and signatures in that protocol's native notation. The contract is what matters; the syntax serves it.
