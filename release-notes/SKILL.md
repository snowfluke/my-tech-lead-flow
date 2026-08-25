---
name: release-notes
description: Write the body of a GitHub release. Use whenever the user asks to cut, tag, publish, draft, or rewrite a release or its notes, in any project. Covers the split between CHANGELOG (complete record) and release notes (user-facing), leading with a measured before/after table when something got faster or smaller, the section order for a first release versus a follow-up, verifying every claim against the published artifact rather than the working tree, editing in place with `gh release edit` so publish workflows do not re-fire, and the house rules: no hard-wrapped lines, no em-dashes, no AI or tool attribution, no `@` mentions, no marketing.
---

# Skill: release notes

Owns the **body** of a GitHub release. The `git-commit` skill owns the mechanics around it: version bump commit, tag, signing, `gh release create`, and the post-publish check.

## The one rule

A CHANGELOG is a complete record for people who already use the project. Release notes are for someone deciding whether to. Pasting one into the other produces a wall nobody reads.

Keep the changelog complete. Link to it from the first line.

## Formatting, non-negotiable

- **Never hard-wrap.** One paragraph is one line, however long. GitHub reflows it; your 80-column breaks render as a ragged left column that looks broken on a wide screen. This is the single most common mistake.
- **No em-dashes.** Use a comma, a colon, a full stop, or parentheses. If a dash is genuinely right, use a spaced hyphen: `word - word`.
- **Bold lead-in on every bullet.** `- **Batched inference** (default on): crops are stacked ...`. The reader scans the bold and stops where it matters.
- **Never `@<name>` or `@<digit>`.** Use backticks or `v4`. An `@` pings a stranger on GitHub. Credit contributors by plain name instead.

## Lead with the numbers

If anything got faster, smaller, or more accurate, that is the first section after the intro, and it is a **table**, not prose. Three columns minimum: old, new, change.

```markdown
## Performance

| Benchmark (receipt.jpg, PP-OCRv6 tiny) | v6.3.0 | v6.4.0 | Change |
| :--- | :--- | :--- | :--- |
| per-line latency | 214 ms | 136 ms | ~36% faster |
| per-line accuracy | 99.48% | 99.48% | unchanged |
```

Name the benchmark and the hardware or input in the header cell, so the number is reproducible instead of a boast. Include the rows that did **not** move; an unchanged-accuracy row is what makes a speed claim credible.

The same shape works for bundle size, memory, install size, or coverage. No numbers to show means no table: do not invent one.

## Before writing

1. **Read the existing notes** if rewriting: `gh release view <tag> --json body -q .body`.
2. **Read the CHANGELOG section** for this version. It is the source, not the output.
3. **Pick the shape.** A first release and a follow-up are different documents.

## Shape: first release

No diff to report, so the notes are an introduction. Nobody installing it has a migration to do, so do not write one.

```
<one paragraph: what it is, who it is for, what it depends on>

## Install                 commands, plus entry points or feature flags if there is more than one
## Quick start             runnable code, real output
## <What is notable>       3-5 themes, not 30 bullets
## Verify this release     only if the project signs or attests
## Known limits            honest, linked to the README
## Credits                 upstream projects, licences, reviewers
```

## Shape: follow-up release

```
<one or two sentences: the theme, plus a link to the CHANGELOG>

## Breaking changes        first if any exist, with before/after and the migration
## Performance             the table, if anything moved
## New                     bold-lead bullets
## Fixed / Security        concrete, with advisory IDs and contributor names
## Verify this release     if the project signs or attests
<closing credit line if the work built on someone else's>
```

Skip any section with nothing in it. A release with one bug fix gets three sentences, not this skeleton padded out.

## Rules

- **Verify every claim against the published artifact.** Install from the registry into a temp directory and run the examples there. Working tree output is not evidence of what shipped. Every number, size, and sample must come from a command you actually ran.
- **Show real output.** Paste what the command printed.
- **Do not showcase a known bug.** If the best example exposes a limitation, choose another.
- **Date it.** The reader needs to know how old the release is.
- **Link out**: docs for each feature, issues and PRs for each fix, the compare URL, the changelog.
- **Credit people and upstream projects** by name, with licences where the project uses someone else's data or code. Call out first-time contributors.
- **State facts.** No "we're excited to", no "huge improvements", no emoji headers, no slop.
- **No AI or tool attribution anywhere.** No `Co-Authored-By`, no "Generated with", no robot emoji, in the notes, the tag message, or any commit along the way.

## Publishing

**Edit in place. Never delete and recreate.**

```bash
gh release edit <tag> --notes-file notes.md
```

Recreating a release fires `release: published` again. If the repo publishes to a registry on that event, the re-run fails on a duplicate version and can leave one registry ahead of the other. `gh release edit` fires `release: edited`, which nothing normally listens for. Check first:

```bash
grep -A3 "^on:" .github/workflows/*.yml | grep -B1 -A2 release
```

Write the notes to a scratch file, not into the repo. The notes are GitHub state; the changelog is the committed record.

## After publishing

- Re-read the live body: `gh release view <tag> --json body -q .body`.
- Confirm no workflow re-fired: `gh run list --limit 3`.
- Confirm the registry has the version, and that attestations or signatures attached.

## Checklist

- [ ] No hard-wrapped paragraphs (one paragraph, one line)
- [ ] No em-dashes anywhere
- [ ] Bold lead-in on every bullet
- [ ] Measured change presented as an old/new/change table, including rows that did not move
- [ ] Correct shape for a first versus follow-up release
- [ ] Breaking changes first, with a migration, if any exist
- [ ] Every code sample run against the installed package, output pasted verbatim
- [ ] Every number traced to a command, not to memory or an older doc
- [ ] No example that displays a known bug
- [ ] Install instructions present
- [ ] Links: docs, issues, compare URL, changelog
- [ ] Contributors and upstream projects credited by name, no `@`
- [ ] No AI or tool attribution anywhere
- [ ] Published with `gh release edit`, not delete and recreate
- [ ] Live body re-read, no workflow re-fired
