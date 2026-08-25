---
name: release-notes
description: Write the body of a GitHub release. Use whenever the user asks to cut, tag, publish, draft, or rewrite a release or its notes, in any project. Covers the split between CHANGELOG (complete record) and release notes (user-facing), the section order for a first release versus a follow-up, verifying every claim against the published artifact rather than the working tree, editing in place with `gh release edit` so publish workflows do not re-fire, and the house rules: no AI or tool attribution, no `@` mentions, no marketing.
---

# Skill: release notes

Owns the **body** of a GitHub release. The `git-commit` skill owns the
mechanics around it: version bump commit, tag, signing, `gh release create`,
and the post-publish check.

## The one rule

A CHANGELOG is a complete record for people who already use the project. Release
notes are for someone deciding whether to. Pasting one into the other produces
a wall nobody reads.

Keep the changelog complete. Link to it from the bottom of the notes.

## Before writing

1. **Read the existing notes**, if you are rewriting: `gh release view <tag> --json body -q .body`.
2. **Read the CHANGELOG section** for this version. It is the source, not the output.
3. **Decide which shape applies** (below). A first release and a patch release
   are different documents.

## Shape: first release (0.1.0, 1.0.0 of something new)

There is no diff to report, so the notes are an introduction. Nobody installing
it has a migration to do, so do not write one.

```
<one paragraph: what it is, who it is for, what it depends on>

## Install
<commands, and entry points or feature flags if there is more than one>

## Quick start
<runnable code, real output>

## <What is notable>       3-5 themes, not 30 bullets
## Verify this release     only if the project signs or attests
## Known limits            honest, linked to the README
## Credits                 upstream projects, licences, reviewers
<link to CHANGELOG.md>
```

## Shape: follow-up release

Lead with what forces the reader to act.

```
<one or two sentences: the theme of this release>

## Breaking changes        first, with before/after and the migration
## Highlights              2-4 changes worth a paragraph each
## Fixed                   terse list, link issues
## Full changelog          link, plus the compare URL
```

Skip any section with nothing in it. A release with one bug fix gets three
sentences, not this skeleton padded out.

## Rules

- **Verify every claim against the published artifact.** Install the package
  from the registry into a temp directory and run the examples there. Working
  tree output is not evidence of what shipped. Every number, size, and code
  sample in the notes must come from a command you actually ran.
- **Show real output.** Paste what the command printed, not what it should print.
- **Do not showcase a known bug.** Pick examples that display the project well
  and are still true. If the best example exposes a limitation, choose another.
- **Date it.** The reader needs to know how old the release is.
- **Link out**: docs for each feature, issues and PRs for each fix, the
  compare URL, the changelog.
- **Credit people and upstream projects**, with licences where the project
  depends on someone else's data or code.
- **State facts.** No "we're excited to", no "huge improvements", no emoji
  headers, no slop.
- **Never `@<name>` or `@<digit>`.** Use backticks or `v4` instead. An `@` in
  release notes pings a stranger on GitHub.
- **No AI or tool attribution anywhere.** No `Co-Authored-By`, no "Generated
  with", no 🤖, no "written by an assistant" line, in the notes, the tag
  message, or any commit made along the way.

## Publishing

**Edit in place. Never delete and recreate.**

```bash
gh release edit <tag> --notes-file notes.md
```

Recreating a release fires `release: published` again. If the repo publishes to
a registry on that event, the re-run fails on a duplicate version, and can leave
one registry ahead of the other. `gh release edit` fires `release: edited`,
which nothing normally listens for. Check before you touch a published release:

```bash
grep -A3 "^on:" .github/workflows/*.yml | grep -B1 -A2 release
```

Write the notes to a scratch file, not into the repo. The notes are GitHub
state; the changelog is the committed record.

## After publishing

- Re-read the live body: `gh release view <tag> --json body -q .body`.
- Confirm no workflow re-fired: `gh run list --limit 3`.
- Confirm the registry has the version, and that attestations or signatures
  attached if the project produces them.

## Checklist

- [ ] Read the CHANGELOG section and the existing notes
- [ ] Correct shape for a first versus follow-up release
- [ ] Breaking changes first, with a migration, if any exist
- [ ] Every code sample run against the installed package, output pasted verbatim
- [ ] Every number traced to a command, not to memory or to an older doc
- [ ] No example that displays a known bug
- [ ] Install instructions present
- [ ] Links: docs, issues, compare URL, changelog
- [ ] Credits and licences for upstream work
- [ ] No `@<name>` or `@<digit>` anywhere
- [ ] No AI or tool attribution anywhere
- [ ] Published with `gh release edit`, not delete and recreate
- [ ] Live body re-read, no workflow re-fired
