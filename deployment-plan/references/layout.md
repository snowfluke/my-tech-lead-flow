# Deployment plan layout

The runbook is a folder. Drop a section file that does not apply to the stack
(for example no TLS for an internal-only service), and keep the numbering
contiguous.

```text
docs/deployment-plan/
  _index.md                   project name, version, date, status, table of contents
  01-environments.md
  02-infrastructure.md
  03-initial-deployment.md
  04-release-updates.md
  05-rollback.md
  06-database-reset.md        always present
  07-database-debugging.md
```

What each part holds:

- **`_index.md`**: project name, version, date, status, and the table of contents.
- **`01-environments.md`**: table of env → URL/host → purpose → who deploys.
- **`02-infrastructure.md`**: topology (a diagram or component list), what each component is, network boundaries.
- **`03-initial-deployment.md`**: sub-stepped as prerequisites; registry auth; environment variables (the full annotated set); start services; run migrations; seed; configure reverse proxy; set up TLS (issue cert → DH params → swap to HTTPS config → apply → verify).
- **`04-release-updates.md`**: standard update (no schema change); update with schema changes (run migrations against the new image before starting the app); pinning to a specific version; troubleshooting a failed update (crash loop, image-not-recreated, auth failures, missing env).
- **`05-rollback.md`**: revert the image tag; database revert caveat and who to contact.
- **`06-database-reset.md`**: a dedicated, always-present section (every plan has it, even if the project thinks it won't need one). Cover, in this order:
   - **Environment gating.** A table of env → reset allowed? → seed used (dev / QA). Reset is permitted on **dev / test / SIT / UAT only**; production is explicitly forbidden, and say so in bold. If a guarded reset API exists (per the technical specs), state that it is disabled/unmounted in prod, not merely access-controlled.
   - **What "initial state" means.** Define it precisely: schema at the latest migration plus the seed dataset applied. QA's request "reset the data to the initial state" maps to exactly this procedure.
   - **The reset procedure**, host-aware. Number the steps and, when the DB is on a separate VM, mark which host each command runs on. The canonical order: (1) stop or drain the app so no writes race the reset and the connection pool is dropped; (2) wipe: drop schema / truncate, with a one-line backup-first warning; (3) re-migrate to head; (4) reseed with the environment's seed (dev or QA); (5) restart the app and clear any cache; (6) verify via the health endpoint and a known seed row. Give the copy-paste commands for each, with real service/host names.
   - **Seed selection.** Where the dev seed and QA seed live, how they differ, and how to choose one (env var, flag, or separate seed command). Note they must be idempotent and version-controlled.
   - **Via the reset API vs manual.** If the reset-state API is available in this environment, give the guarded `curl` against it as the primary path and the manual host commands as the fallback for when the app is down.
- **`07-database-debugging.md`** (or the system's data store): a cookbook covering interactive session; one-off queries; health/size checks; migration inspection; dump & restore; logs; quick data-inspection shortcuts; container/image sizes; common failure recovery. Reference the Database State Reset section above rather than repeating the reset commands.

## Older projects

An older project keeps the runbook in one `docs/DEPLOYMENT_PLAN.md`. To migrate,
move each numbered section into its file above and fix the links that pointed
into the old file.
