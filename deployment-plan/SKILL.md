---
name: deployment-plan
description: Produce a DEPLOYMENT_PLAN.md operational runbook by first grilling the user on infrastructure, environments, secrets, release flow, and rollback until every gap is resolved, then writing the document. Models the Tatanan/Terral deployment plan — environments, infra overview, initial deploy, release updates, rollback, and a database debugging cookbook with copy-paste commands. Use when the user wants a deployment plan, deployment runbook, ops/release documentation, or asks to "write a DEPLOYMENT_PLAN".
---

# Deployment Plan

Two phases: **grill first, then write.** A deployment runbook is only useful if it reflects the real infrastructure and the operator can paste its commands verbatim and have them work. So extract the truth before writing a line of the document.

## Phase 1 — Grill

Interview the user relentlessly about how this system actually deploys, one question at a time, walking each branch until resolved. For every question, give your recommended answer and explain the trade-off, but don't move on until they confirm.

**Inspect before asking.** Read the repo first — `docker-compose*.yml`, `Dockerfile`, `.github/workflows/`, `deploy/`, nginx configs, `.env.example`, migration setup, README, and any existing `CLAUDE.md`. Every fact you can read, read; don't ask what the repo already answers. Ask only to fill genuine gaps and to confirm inferences.

Cover, at minimum (skip what's irrelevant to this stack, probe what's load-bearing):

- **Environments.** How many (dev / test / staging / prod), their URLs/hosts, who can deploy to each, and how they differ.
- **Infrastructure.** Hosting (VPS / cloud / k8s / PaaS), what runs where, the topology (app, db, cache, proxy, object storage), and the network boundaries between them. **Pin down whether the app and the database live on the same host or separate VMs** — if separate, capture the DB host/port, how the app reaches it (private network, security group, allowlisted IP), and whether DB commands must run from the DB VM or can run remotely from the app VM. Cross-VM topology is the common cause of a reset going wrong (commands run against the wrong host, or the app keeps a stale connection pool after the DB is wiped).
- **Artifacts & registry.** How images/builds are produced (CI? manual?), where they're stored (GHCR / ECR / Docker Hub), tagging scheme, and how a host authenticates to pull.
- **Configuration & secrets.** The full env-var set, which are required vs optional, how secrets are generated and injected, and what must never be committed.
- **Initial deploy.** Prerequisites on a fresh host, the exact bring-up sequence, first-run migrations, seeding, and the admin/bootstrap credentials.
- **Reverse proxy & TLS.** Proxy choice, domains, certificate issuance/renewal, and security headers.
- **Release updates.** The update flow with and without schema changes, how migrations run against a new image safely, version pinning, and how a deploy is verified. **Establish a single migration/seed command that resolves its own paths and connection string** — whatever the stack's idiom is (a make target, `manage.py migrate`, a `rake`/`mix`/`artisan`/`bun run` script, a migrate binary) shipped in the image. Reject any runbook step that hardcodes an absolute migration path or inlines a raw SQL file read (see the anti-pattern in the writing rules); those break the moment the container layout or image type (e.g. distroless) changes and force the operator to spelunk for files at 2am.
- **Rollback.** How to revert an image, what happens to the database on rollback (destructive migrations? down-migrations? manual?), and who to contact.
- **Operations.** DB access for debugging, backup/restore, log access, and health checks.
- **Database state reset.** This is load-bearing for QA: how the database is wiped, re-migrated, and reseeded back to a known initial state, and which seed (dev vs QA) each environment uses. Establish which environments allow a reset (dev / test / SIT / UAT only — never prod), who triggers it, whether it goes through a guarded reset API (see the technical specs) or a manual runbook, and the exact order of operations across the app and DB hosts. Capture what must happen to the app after a wipe (restart, drain connection pool, clear cache) so it doesn't keep serving against a dropped schema. Confirm the seed datasets are version-controlled and idempotent.

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
8. **Database State Reset** — a dedicated, always-present section (every plan has it, even if the project thinks it won't need one). Cover, in this order:
   - **Environment gating.** A table of env → reset allowed? → seed used (dev / QA). Reset is permitted on **dev / test / SIT / UAT only**; production is explicitly forbidden, and say so in bold. If a guarded reset API exists (per the technical specs), state that it is disabled/unmounted in prod, not merely access-controlled.
   - **What "initial state" means.** Define it precisely: schema at the latest migration plus the seed dataset applied. QA's request "reset the data to the initial state" maps to exactly this procedure.
   - **The reset procedure**, host-aware. Number the steps and, when the DB is on a separate VM, mark which host each command runs on. The canonical order: (1) stop or drain the app so no writes race the reset and the connection pool is dropped; (2) wipe — drop schema / truncate, with a one-line backup-first warning; (3) re-migrate to head; (4) reseed with the environment's seed (dev or QA); (5) restart the app and clear any cache; (6) verify via the health endpoint and a known seed row. Give the copy-paste commands for each, with real service/host names.
   - **Seed selection.** Where the dev seed and QA seed live, how they differ, and how to choose one (env var, flag, or separate seed command). Note they must be idempotent and version-controlled.
   - **Via the reset API vs manual.** If the reset-state API is available in this environment, give the guarded `curl` against it as the primary path and the manual host commands as the fallback for when the app is down.
9. **Inspecting & Debugging the Database** (or the system's data store) — a cookbook: interactive session; one-off queries; health/size checks; migration inspection; dump & restore; logs; quick data-inspection shortcuts; container/image sizes; common failure recovery. Reference the Database State Reset section above rather than repeating the reset commands.

### Writing rules

- Commands must reflect reality: real container/service names from the compose file, real image refs, real env-var names. No placeholders where a real value is known.
- Every destructive command carries a one-line warning about what it deletes and how to back up first.
- **Never document migrations or seeding as a hardcoded path or an inline raw-SQL read**, in any language. The migration and seed steps must invoke the project's own runner, which resolves the migrations location relative to its own module and reads the connection string from the environment. State the migrate and seed steps as one stable command each (whatever the stack's equivalent is: a make target, a manage.py command, a `mix`/`rake`/`artisan`/`bun run` script, a migrate binary), never as an operator-supplied file path. The failure mode this prevents: an operator who cannot find the migrations inside a distroless or minimal image and resorts to piping a specific `.sql` file by absolute path through a one-liner, applying schema partially and outside the migration ledger.

  Good (a single command; the app finds its own files and config):

  ```bash
  docker compose exec app <project migrate command>   # e.g. bun run db:migrate, ./manage.py migrate, migrate -path ... up
  docker compose exec app <project seed command>
  ```

  Bad (hardcoded path, inlined credentials, raw SQL, single file only) — illustrated in TypeScript/Bun, but the anti-pattern is language-independent:

  ```bash
  docker compose exec app bun -e "const {SQL}=require('bun');const fs=require('fs');
  const db=new SQL('postgres://user:pass@10.0.0.1:5432/db');
  await db.unsafe(fs.readFileSync('/app/src/db/migrations/0000_initial.sql','utf8'));"
  ```

  If the only working command during an incident was the bad form, treat that as a deployment defect to fix in the image (ship a real migration runner behind a stable command), not as the runbook's recommended path.
- Annotate, number, and order steps so an operator can follow top-to-bottom on a fresh host.
- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If the document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
- Write to `docs/DEPLOYMENT_PLAN.md` (or where the project keeps ops docs); if one exists, read and update it in place rather than clobbering, and report what changed.
