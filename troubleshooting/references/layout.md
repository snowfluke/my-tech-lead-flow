# Troubleshooting guide layout

The guide is a folder. Seam files follow this project's risk order, most likely
and most damaging first, so the numbering differs per project.

```text
docs/troubleshooting/
  _index.md                  header and table of contents only
  01-triage.md               how to use the guide, the fast triage checklist, how to add an entry
  02-<riskiest-seam>.md      for example 02-database.md
  03-<next-seam>.md          for example 03-build-and-deploy.md
```

Typical seams: database, reverse proxy and TLS, build and deploy, external
integrations, auth, app runtime. Use the seams this system has.

## `01-triage.md`

- How to use the guide. It is indexed by symptom. Its scaffolded entries come from the architecture, not from incidents.
- The fast triage checklist. Is the service up? Are the health checks green? Was there a recent deploy? What do the logs say?
- How to add an entry. Diagnose a real incident, for example with `diagnose`. Then promote the matching scaffolded entry to confirmed, with the date and a reference. If no entry matches, add a new one.

## Entry format

Every seam file is a list of entries in this shape:

```markdown
### <Symptom as the operator sees it>

**Looks like:** <exact error text / status code / observable behaviour>
**Likely causes:** <ranked list, most common first>
**Confirm:** <command(s) to run to identify which cause it is>
**Fix:** <command(s) or steps for each cause>
**Prevent:** <config/check that stops recurrence>
**Status:** scaffolded, not yet seen in production
```

## Older projects

An older project keeps the guide in one `docs/TROUBLESHOOTING.md`. To migrate,
move each seam heading and its entries into its own file, and the how-to-use
and triage parts into `01-triage.md`.
