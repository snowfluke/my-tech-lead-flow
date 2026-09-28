---
name: troubleshooting
description: Produce a troubleshooting guide in docs/troubleshooting/, one file per architectural seam, organized by symptom. Before real incidents exist, it maps the system's seams with the user (database, cache, proxy, external APIs, auth, build and deploy) and seeds the likely failures at each seam. The guide grows as real incidents land. It links to docs/deployment-plan/ instead of repeating it. Use when the user wants a troubleshooting guide, a runbook of common problems, an ops FAQ, or asks to "write a TROUBLESHOOTING".
---

# Troubleshooting Guide

A troubleshooting guide is as good as the failures it knows. Before real
incidents exist, this skill works from the architecture. It finds where this
system most likely breaks, at its seams, and seeds an entry for each. Say
plainly that the result is a skeleton. Real incidents replace guesses over time.

Two phases: map the seams with the user, then write the guide by symptom.

## Phase 1: Map the seams

Read the repo first. Ask only what the files cannot tell you. Read:

- `docs/deployment-plan/`, or `DEPLOYMENT_PLAN.md` in an older project;
- `README`, `docker-compose*.yml`, `Dockerfile`, the CI workflows, and `.env.example`;
- the technical specs, and `CLAUDE.md` or `AGENTS.md`.

Most production failures sit at a boundary between two components. Map those
boundaries. Settle these points one question at a time, each with a
recommended answer:

- **Topology and seams.** List the components: app, database, cache, queue, reverse proxy, object storage, external APIs, auth provider. List the connections between them. Each connection is a failure point.
- **Observable surface.** Find what a failure looks like to the operator. Collect the error codes and messages and the health endpoints. Find where logs live, and which metrics and alerts exist.
- **Build and deploy seams.** Find where deploys, migrations, image pulls, secret injection, and TLS most likely fail. Link to `docs/deployment-plan/` for what it already covers.
- **Runtime dependencies.** Note the versions of the database engine, the language runtime, and the OS. Note the known sharp edges of each.
- **Existing knowledge.** Ask which failures the user already remembers. Collect troubleshooting notes that already sit in other docs.

Name the riskiest seams, for example no backups, a single point of failure, or
an external dependency with no fallback. The guide lists those first.

## Phase 2: Write the guide by symptom

An operator arrives with an error, not a diagnosis. So index the guide by
symptom. Write `docs/troubleshooting/` in the layout of
[references/layout.md](references/layout.md): one file per seam, each a list
of entries in the entry format there.

Rules:

- **Diagnostic commands are real and runnable** for this stack: real service names, log paths, health URLs, and env vars. The cause may be a guess. The command that checks it must work.
- **Every new entry is `scaffolded`.** A real incident changes the status to confirmed and adds the date and a reference. This keeps guesses apart from tested knowledge.
- **Link to `docs/deployment-plan/`, do not copy it.** For a failure it covers, link to the section, for example `docs/deployment-plan/06-database-reset.md`.
- **Order seam files by risk**, most likely and most damaging first. Number the files in that order.
- `01-triage.md` holds the note on how to use the guide, the fast triage checklist, and how to add an entry.
- No filler and no hedging. Use the `stop-slop` skill on prose when unsure.
- No em dashes. No `--` outside code and CLI flags. No emoji.
- A metadata header line (`**Version:**`, `**Date:**`, `**Status:**`) ends with two spaces. Markdown then shows each line on its own.

## Grow the guide

When someone diagnoses a real incident, for example with the `diagnose` skill,
they record it in its seam file. They promote the matching scaffolded entry to
confirmed, or add a new entry. `01-triage.md` explains this.

Write to `docs/troubleshooting/`. If the guide exists, read it and extend it in
place. Never change a confirmed entry back to scaffolded. If the guide is one
older `docs/TROUBLESHOOTING.md`, ask once whether to migrate it (see
[references/layout.md](references/layout.md)). If the user says no, extend the
single file. Report what you added or changed.
