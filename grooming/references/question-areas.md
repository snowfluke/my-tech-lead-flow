# Question areas (INVEST)

Each letter is a lens. The technical sub-points under it are what engineering asks.

## I: Independent
*Can this story be built, tested, and shipped on its own?*
- What other in-flight stories or teams does this depend on, and which can ship independently?
- Which external systems, APIs, or services are involved; are their contracts stable and documented?
- Are feature flags / config toggles needed to decouple this from other work?
- Does this require a migration or backfill that another story must land first?

## N: Negotiable
*Is the intent clear enough to discuss trade-offs, without over-specifying the solution?*
- What problem does this solve, and for whom? What's explicitly **out** of scope?
- Is this net-new or a change to existing behaviour, and who relies on the current behaviour?
- Where has the BA/PO baked in an implementation choice we could simplify or swap if it's costly?

## V: Valuable
*Does this deliver observable value, and can we tell once it's live?*
- What does success look like in production, and what metric/analytics confirm it?
- What's the cost of *not* doing it, and does the technical approach actually move that needle?
- Observability: what logs, metrics, or alerts must exist for support to operate and prove value?

## E: Estimable
*Do we know enough to size it with confidence?*
- What new entities/fields/states does this introduce? Required vs optional? Defaults? Source of truth and constraints?
- Migration/backfill: what happens to existing rows, and is downtime acceptable?
- Non-functionals: expected volume, throughput, latency, growth, and any SLAs?
- Auth/authz and privacy/compliance: who can do this, how is it enforced, any PII/audit/retention angle?
- What's the riskiest unknown, and can we spike it *before* committing a number?

## S: Small
*Does it fit comfortably in one sprint?*
- Does the story bundle independent concerns that should be separate stories?
- Where's the natural seam to slice a thin, end-to-end (vertical) increment that still ships value?
- Is there hidden work (migration, rollout, A/B, rollback plan, in-flight data/session handling) that inflates this beyond a sprint?

## T: Testable
*Can every acceptance criterion be verified?*
- Is each AC observable and testable? Rewrite any that aren't.
- What are the unhappy paths: empty states, validation failures, permission denials, partial failures, timeouts?
- Boundary values and limits (lengths, counts, ranges, pagination)?
- Idempotency and concurrency: what happens on double-submit or race? What does the user see during loading/error states?
- Definition of Done: which tests, docs, monitoring, and analytics are required to call it shipped?
