---
name: deployment-plan
description: Produce a DEPLOYMENT_PLAN.md operational runbook by first grilling the user on infrastructure, environments, secrets, release flow, and rollback until every gap is resolved, then writing the document. Models the house deployment plan — environments, infra overview, initial deploy, release updates, rollback, and a database debugging cookbook with copy-paste commands. Use when the user wants a deployment plan, deployment runbook, ops/release documentation, or asks to "write a DEPLOYMENT_PLAN".
---

# Deployment Plan

Two phases: **grill first, then write.** A deployment runbook is only useful if it reflects the real infrastructure and the operator can paste its commands verbatim and have them work. So extract the truth before writing a line of the document.

## Phase 1 — Grill

Interview the user relentlessly about how this system actually deploys, one question at a time, walking each branch until resolved. For every question, give your recommended answer and explain the trade-off, but don't move on until they confirm.

**Inspect before asking.** Read the repo first — `docker-compose*.yml`, `Dockerfile`, `.github/workflows/`, `deploy/`, nginx configs, `.env.example`, migration setup, README, and any existing `CLAUDE.md`. Every fact you can read, read; don't ask what the repo already answers. Ask only to fill genuine gaps and to confirm inferences.

Cover, at minimum (skip what's irrelevant to this stack, probe what's load-bearing):

- **Environments.** How many (dev / test / staging / prod), their URLs/hosts, who can deploy to each, and how they differ.
- **Infrastructure.** Hosting (VPS / cloud / k8s / PaaS), what runs where, the topology (app, db, cache, proxy, object storage), and the network boundaries between them.
- **Artifacts & registry.** How images/builds are produced (CI? manual?), where they're stored (GHCR / ECR / Docker Hub), tagging scheme, and how a host authenticates to pull.
- **Configuration & secrets.** The full env-var set, which are required vs optional, how secrets are generated and injected, and what must never be committed.
- **Initial deploy.** Prerequisites on a fresh host, the exact bring-up sequence, first-run migrations, seeding, and the admin/bootstrap credentials.
- **Reverse proxy & TLS.** Proxy choice, domains, certificate issuance/renewal, and security headers.
- **Release updates.** The update flow with and without schema changes, how migrations run against a new image safely, version pinning, and how a deploy is verified.
- **Rollback.** How to revert an image, what happens to the database on rollback (destructive migrations? down-migrations? manual?), and who to contact.
- **Operations.** DB access for debugging, backup/restore, log access, health checks, and the reset procedure.

Surface contradictions as you find them ("the compose file pulls `:latest` but you said releases are version-pinned — which is authoritative?"). Note anything genuinely dangerous (no backups before destructive migration, secrets in the repo, no rollback path) and make sure the plan addresses it.

When every branch is resolved, summarize the decisions back and confirm before writing.

## Phase 2 — Write DEPLOYMENT_PLAN.md

Write a runbook in the structure below. It is operational, not aspirational — every command must be copy-paste-runnable for this project, using its real service names, paths, image refs, and env vars. Use fenced shell blocks with terse `#` comments explaining each step. Adapt section depth to the stack; drop sections that don't apply (e.g. no TLS section for an internal-only service).

1. **Title + summary** — project name, version, date, status.
2. **Table of Contents.**
3. **Environments** — table of env → URL/host → purpose → who deploys.
4. **Infrastructure Overview** — topology (a diagram or component list), what each component is, network boundaries.
5. **Initial Deployment** — sub-stepped: prerequisites; registry auth; environment variables (the full annotated set); start services; run migrations; seed; configure reverse proxy; set up TLS (issue cert → DH params → swap to HTTPS config → apply → verify).
6. **Updating to a New Release** — standard update (no schema change); update with schema changes (run migrations against the new image before starting the app); pinning to a specific version; troubleshooting a failed update (crash loop, image-not-recreated, auth failures, missing env).
7. **Rollback** — revert the image tag; database revert caveat and who to contact.
8. **Inspecting & Debugging the Database** (or the system's data store) — a cookbook: interactive session; one-off queries; health/size checks; migration inspection; dump & restore; logs; quick data-inspection shortcuts; container/image sizes; common failure recovery; full reset procedure.

### Writing rules

- Commands must reflect reality: real container/service names from the compose file, real image refs, real env-var names. No placeholders where a real value is known.
- Every destructive command carries a one-line warning about what it deletes and how to back up first.
- Annotate, number, and order steps so an operator can follow top-to-bottom on a fresh host.
- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If the document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
- Write to `docs/DEPLOYMENT_PLAN.md` (or where the project keeps ops docs); if one exists, read and update it in place rather than clobbering, and report what changed.
