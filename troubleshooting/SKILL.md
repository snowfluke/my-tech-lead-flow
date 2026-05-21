---
name: troubleshooting
description: Produce a TROUBLESHOOTING.md guide organized by symptom. With no real incident corpus yet, it grills the user to map the system's architecture and seams (DB, cache, proxy, external APIs, auth, build/deploy), then scaffolds the likely failure modes at each seam as a living skeleton to grow as real incidents land. References DEPLOYMENT_PLAN.md rather than duplicating it. Use when the user wants a troubleshooting guide, runbook of common problems, an ops FAQ, or asks to "write a TROUBLESHOOTING".
---

# Troubleshooting Guide

A troubleshooting guide is only as good as the failures it knows about. There's no real incident corpus yet, so this skill **scaffolds from architecture**: it reasons about where *this* system most plausibly breaks — at its seams — and seeds those as entries. Be explicit that the output is a living skeleton, seeded from architecture and not yet from real incidents; it grows as actual failures get captured.

Two phases: **grill to map the system, then scaffold by symptom.**

## Phase 1 — Grill to map the seams

Inspect the repo first, then ask only what you can't read. Read `DEPLOYMENT_PLAN.md`, `README`, `docker-compose*.yml`, `Dockerfile`, CI workflows, `.env.example`, architecture/technical-spec docs, and `CLAUDE.md`. Most production failures live at boundaries between components, so build a map of those boundaries.

Resolve, one question at a time (recommend an answer each):

- **Topology & seams.** What are the components (app, db, cache, queue, reverse proxy, object storage, external APIs, auth provider) and the connections between them? Each connection is a failure point.
- **Observable surface.** What does a failure *look like*? Error codes/messages the system emits, health-check endpoints, where logs live, what metrics/alerts exist. Symptoms must be described as the operator actually sees them.
- **Build & deploy seams.** Where do deploys, migrations, image pulls, env/secret injection, and TLS most plausibly fail? (Cross-reference `DEPLOYMENT_PLAN.md` — don't re-derive what it documents.)
- **Runtime dependencies.** Versions/runtimes (DB engine, language runtime, OS) and known sharp edges of each.
- **Existing knowledge.** Even without a corpus: any failure the user already remembers, any troubleshooting already embedded in other docs.

Surface the riskiest seams (no backups, single point of failure, an external dependency with no fallback) so the scaffold prioritizes them.

## Phase 2 — Scaffold TROUBLESHOOTING.md by symptom

Organize by **symptom**, because that's how an operator arrives: they have an error, not a diagnosis. For each architectural seam, write one or more entries in this shape:

```markdown
### <Symptom as the operator sees it>

**Looks like:** <exact error text / status code / observable behaviour>
**Likely causes:** <ranked list, most common first>
**Confirm:** <command(s) to run to identify which cause it is>
**Fix:** <command(s) or steps for each cause>
**Prevent:** <config/check that stops recurrence>
**Status:** scaffolded · not yet seen in production
```

Rules:

- **Diagnostic commands must be real and runnable** for this stack — real service names, log paths, health URLs, env vars. The *cause* may be hypothesized, but the command to check it must work.
- **Mark every entry `scaffolded`** until a real incident confirms it. When an entry is later confirmed by an actual incident, the status changes and the entry should record the date/reference. This keeps speculation visibly separate from battle-tested knowledge.
- **Reference, don't duplicate, `DEPLOYMENT_PLAN.md`.** For deploy/DB-recovery failures it already covers, link to the section (`see DEPLOYMENT_PLAN.md §4.4`) instead of copying.
- **Prioritize by seam risk**, not alphabetically. Lead with the failures that are most likely and most damaging for this architecture.
- Group entries under headings by component/seam (Database, Reverse proxy & TLS, Build/Deploy, External integrations, Auth, App runtime).
- Open with a "How to use this guide" note stating it's symptom-indexed and architecture-seeded, and a fast triage checklist (is the service up? health checks green? recent deploy? logs saying what?).
- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If the document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.

## Growing the guide

Close the document with a short "Adding an entry" section: when a real incident is diagnosed (e.g. via the `/diagnose` skill), capture it here — promote a matching scaffolded entry to confirmed, or add a new one — so the guide converges on reality over time.

Write to `docs/TROUBLESHOOTING.md` (or where ops docs live). If one exists, read and extend in place rather than clobbering; never downgrade a confirmed entry back to scaffolded. Report what was added or changed.
