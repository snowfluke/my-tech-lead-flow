---
name: code-review
description: Act as a tech lead reviewing a pull request against the project's own coding standards and review checklist, in any language. Discovers the repo's standards docs, checks out the PR branch in an isolated git worktree, runs the project's test / lint / format / type-check gates, verifies the diff against the checklist and any referenced acceptance criteria, then posts a structured review with severity-tagged findings. Use when the user asks to review a PR, review a branch, or do code review.
---

# Code Review

Review a PR the way a tech lead does: ground every finding in the project's own documented standards, prove the code builds and passes its gates, and deliver an actionable, navigable review. Language- and stack-agnostic — detect the toolchain, don't assume one.

## 1. Discover the project's standards

**Always read the `README` first**, before anything else. It is mandatory and non-negotiable: read the repo's `README.md` (and any `README` it points to in subdirectories relevant to the PR) to understand what the project is, how it's built and run, and which conventions it declares. Never start a review without it.

Then the standards are the source of truth. Do not raise findings for rules the project hasn't written down; do not skip rules it has. Before reviewing, locate them — check the repo root, `docs/`, `.github/`, and `CONTRIBUTING.md`:

| Looking for | Common names |
| --- | --- |
| Coding standards | `CODING_STANDARD(S).md`, `STYLE_GUIDE.md`, `CONTRIBUTING.md`, `docs/coding-*.md` |
| Review checklist | `CODE_REVIEW_CHECKLIST.md`, `PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE.md` |
| Architecture / specs | `docs/technical-specs/`, `TECHNICAL_SPECIFICATION*.md`, `ARCHITECTURE.md`, ADRs under `docs/adr/` |
| Stories / acceptance criteria | `docs/business/`, `USER_STORY.md`, `ACCEPTANCE_CRITERIA.md` |
| Task breakdown | `TASK_BREAKDOWN.md` |
| API specs | `docs/api-specs/`, `openapi.*`, `*.openapi.json` |

Also read the repo's `CLAUDE.md` / `AGENTS.md` if present — it often encodes the real rules. If no standards docs exist, say so and review against the conventions visible in the surrounding code instead of inventing rules.

## 2. Check out the PR in an isolated worktree

Use `git worktree` so the PR branch never disturbs the user's current checkout — other agents can keep working in parallel.

```bash
git fetch origin
PR_BRANCH=$(gh pr view <number> --json headRefName --jq '.headRefName')
git worktree add "/tmp/pr<number>-review<N>" "origin/$PR_BRANCH"
```

All file reads (`read`/`glob`/`grep`) on PR source must use the worktree path. `gh pr diff|view|checks` work from anywhere. Clean up when done:

```bash
git worktree remove "/tmp/pr<number>-review<N>" --force
```

For a local branch with no PR, worktree the branch ref directly and review the diff against the base branch (`git diff <base>...<branch>`).

## 3. Gather PR context

```bash
gh pr view <number> --json title,body,author,baseRefName,headRefName,files,additions,deletions,commits
gh pr diff <number>
gh pr checks <number>
gh pr view <number> --json mergeStateStatus,mergeable
```

- **Scope check.** If the PR description references a task card (e.g. in `TASK_BREAKDOWN.md`), cross-reference each changed file against what the card says should change. Flag files with no clear connection to the task as a BLOCKER (`F0`, so it sorts first) unless the description justifies the touch.
- **Mergeability.** If not mergeable / has conflicts, raise a BLOCKER: the branch must be rebased on the base before merging. Don't approve an unmergeable PR.
- Read prior review rounds and conversation to avoid re-raising resolved points.

## 4. Run the verification gate

Run the project's own gates in the worktree. **Detect the toolchain — never hard-code `npm`/`bun`.** Prefer, in order: a documented command in `CLAUDE.md`/README/`CONTRIBUTING.md` → a script in the manifest → the ecosystem default.

| Ecosystem | Detect via | Typical type-check / lint / format / test |
| --- | --- | --- |
| JS/TS | `package.json`, lockfile (`bun.lock`→bun, `pnpm-lock`→pnpm, `yarn.lock`→yarn, else npm) | `<pm> run type-check` · `lint` · `fmt`/`format` · `test`; else `tsc --noEmit`, `eslint .`, `prettier --check .` |
| Rust | `Cargo.toml` | `cargo check` · `cargo clippy -- -D warnings` · `cargo fmt --check` · `cargo test` |
| Go | `go.mod` | `go vet ./...` · `golangci-lint run` · `gofmt -l .` · `go test ./...` |
| Python | `pyproject.toml`/`setup.cfg` | `mypy`/`pyright` · `ruff check`/`flake8` · `ruff format --check`/`black --check` · `pytest` |
| Java/Kotlin | `pom.xml`/`build.gradle` | `mvn verify` / `gradle build check` |

Run type-check → lint → format-check → test (then build if the project has one). Report each result. A failing gate is a finding (BLOCKER if the gate is required by the checklist). If a manifest defines a single aggregate script (e.g. `complete-check`, `ci`), prefer it. If the toolchain can't run (missing deps, unsupported here), say so explicitly rather than claiming a pass.

## 5. Review the diff

Walk the diff against the discovered standards and checklist, in this order:

1. **Checklist.** Go through the review checklist item by item; every applicable item must hold in the diff.
2. **Architecture & layering.** Layer boundaries, module structure, no business logic where the standards forbid it, file-size limits, no duplication of existing utilities.
3. **Correctness & safety.** Error handling, input validation, auth/permission enforcement, transactions/atomicity, concurrency, secrets, injection.
4. **API contract.** If endpoints changed and specs exist, verify method/path/request/response/status/pagination match the spec; deviations need justification in the PR.
5. **Acceptance criteria.** First confirm the cited AC IDs are real, not fabricated or stale: `python scripts/check_ac_refs.py <pr-files> --business-dir docs/business` (non-zero exit lists any AC ID the PR cites that doesn't exist in the repo's business docs). Then, for every AC the PR references, read its full Given/When/Then and trace each THEN to the code — exact displayed text/labels/messages (match wording verbatim, even non-English), conditional/empty states, role constraints, real-data vs hardcoded. A mismatch is a finding; quote the specified text.
6. **Tests.** Each referenced AC / behaviour has a test (respect project norms — e.g. some projects make frontend tests optional). Migrations/schema changes are consistent and rebased.

## 6. Post the review

Write the body with the Write tool to a temp file and post via `--body-file` — **never** an inline heredoc, which mangles backticks:

```bash
gh pr review <number> --request-changes --body-file /tmp/pr<number>-review.md   # any finding
gh pr review <number> --approve         --body-file /tmp/pr<number>-review.md   # zero findings
rm /tmp/pr<number>-review.md
```

`--request-changes` if there is **any** finding, even a nit; `--approve` only at zero findings. Never end on a plain `--comment`.

### Finding format

Stable IDs (`F1`, `F2`, …) that persist across rounds. Severity `BLOCKER` (must fix) or `NIT` (encouraged). One finding per logical problem.

````
### F<N> · <short title> · <BLOCKER|NIT>

**File:** `<path>:<line>`
**Rule:** [<doc> <section>](<link>) — "<rule quoted verbatim>"
**Fix:** <one sentence>

```diff
- <wrong code from PR>
+ <suggested replacement>
```
````

Always provide a `diff` block, never `// wrong` / `// correct` comments. Quote the rule verbatim with a link to the standards doc (use repo-relative `../blob/<base>/...` links; append `?plain=1#L<n>` for line anchors in markdown). If a finding maps to no written rule, mark it as a suggestion, not a standards violation.

### Multi-turn rounds

Open every round with a status table, then detail only `OPEN` findings:

```markdown
## Round N — Request Changes

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F1 | ...     | BLOCKER  | OPEN/RESOLVED |
```

IDs never change across rounds. Mark `RESOLVED` only after confirming the fix in the new diff. NITs may stay `OPEN` and still allow an approve once all BLOCKERs are resolved.

### After posting

- If the review requests changes with an open BLOCKER and the project's flow expects it, convert the PR to draft: `gh pr ready <number> --undo`.
- **Move the linked issue's board card to match the verdict.** Check whether the PR closes an issue and whether that issue is on a project board:
  `gh pr view <number> --json closingIssuesReferences,projectItems`. If it links an issue that is on a board, set the issue's `Status` field to reflect the result, using the board's own column names:
  - Request Changes -> back to the in-progress column (e.g. `In Progress`), so the author picks it up.
  - Approve -> advance toward done (e.g. `In Review` to a ready-to-merge or `Done` column, per the board's convention; many boards only reach `Done` on merge).

  Move it with `gh project item-edit --id <item-id> --field-id <status-field> --project-id <pid> --single-select-option-id <option>`. If the PR links no issue, or the issue is not on a board, skip this silently; never create a card here.
- Fill in the PR's reviewer sign-off / checklist boxes if the template has them, per project convention. Don't add a bot/agent as a human reviewer.
- Remove the worktree.

## Comment rules

- No AI slop, no filler. Be concise; every sentence informs. Always cite file and line.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`). No emoji. Professional tone.
- Quote the specific standard violated; link the doc. Group related issues under one finding.
- Respect documented exceptions (intentional mocks, deferred-TODO patterns, scaffold cards) — read the task/standards before flagging them.
