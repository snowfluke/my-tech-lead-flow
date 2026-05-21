---
name: git-commit
description: Use after completing a task when all verifications pass. Covers verification commands, splitting into logical commits, explicit file staging, Conventional Commits format with 80-char line cap, no `@` mentions in messages, and no Co-Authored-By trailers.
---

# Skill: git-commit

## When to Use

You have completed a task, all verifications have passed, and you need to commit the changes.

## Steps

1. **Run final verification — all must pass:**

   ```bash
   bun run type-check
   bun test
   bun run lint
   bun run fmt
   ```

   If any fails, stop and fix the issue before committing.

2. **Check what will be staged:**

   ```bash
   git status
   git diff --stat
   ```

3. **Split into logical commits.** Before staging, scan the diff and group changes by intent. **Do not put unrelated changes into one commit.** A commit should answer a single "why."

   Common splits:
   - Bug fix vs version bump → two commits
   - Source code change vs test additions for an unrelated module → two commits
   - Refactor vs new feature → two commits
   - Code change vs docs/CHANGELOG update for that same code → can be one commit
   - Code change vs unrelated formatting noise → two commits (or revert the noise)

   If the working tree has multiple intents, commit them in sequence:

   ```bash
   # Commit 1: the fix
   git add src/auth/session.ts tests/auth/session.test.ts
   git commit -m "fix(auth): handle expired refresh token gracefully"

   # Commit 2: the version bump (separate intent)
   git add package.json jsr.json
   git commit -m "chore: bump version to 5.4.2"
   ```

   When uncertain whether two changes belong together, the test is: "Could someone want to revert one without the other?" If yes, split.

4. **Stage the relevant files for the current commit.** Be explicit — do not use `git add -A` blindly:

   ```bash
   git add apps/api/src/modules/projects/
   git add apps/api/src/db/migrations/0003_add_project_archive.sql
   # etc.
   ```

   **Never stage:**
   - `.env` files
   - `*.pem` key files
   - `bun.lock` changes for unrelated packages
   - Build output (`dist/`, `.next/`)

5. **Compose the commit message** using Conventional Commits:

   Format: `<type>(<scope>): <subject>`

   | Type       | Use when                                  |
   | ---------- | ----------------------------------------- |
   | `feat`     | New feature or behavior                   |
   | `fix`      | Bug fix                                   |
   | `refactor` | Code change with no behavior change       |
   | `test`     | Adding or fixing tests                    |
   | `docs`     | Documentation changes only                |
   | `chore`    | Build config, tooling, dependency updates |
   | `perf`     | Performance improvement                   |

   Scope: the module or layer changed (e.g., `auth`, `tasks`, `gantt`, `db`, `ci`)

   Subject rules:
   - Imperative mood: "add", "fix", "refactor" — not "added" or "fixing"
   - **Max 80 characters for the entire first line** (`type(scope): subject [ID]` combined). The husky hook enforces this for the subject line.
   - No period at end
   - Reference task ID when applicable: `[BE-S2-02]`
   - **Never write `@<name>` or `@<digit>` anywhere in the message.** GitHub renders `@something` as a user mention and notifies whoever owns that handle. For version pins, write `v4` / `v5`, `major 4`, or wrap in backticks (`` `@4` ``). The same rule applies to commit bodies, PR titles, PR bodies, issue comments, and release notes.

   Body rules (for multi-line commits):
   - **Every line in the body is also capped at 80 characters.** Hard-wrap long sentences manually.
   - One blank line between subject and body.
   - One blank line between paragraphs in the body.

   **Before writing the commit, count the longest line in the full message:**

   ```bash
   git commit -m "$(cat <<'EOF'
   <your-commit-message>
   EOF
   )" --dry-run >/dev/null 2>&1 || true
   # Then sanity-check line lengths:
   awk '{ if (length > 80) print "TOO LONG (" length "): " $0 }' <<'EOF'
   <paste full message here>
   EOF
   ```

   For quick subject-only checks:

   ```bash
   echo -n "chore(auth): remove readme artifact and fix ErrorBoundary [FE-AUTH-06]" | wc -c
   # must be ≤ 80
   ```

6. **Create the commit:**

   ```bash
   git commit -m "feat(projects): add project creation endpoint [BE-S2-02]"
   ```

   For multi-line commits (when the "why" is non-obvious):

   ```bash
   git commit -m "feat(tasks): enforce finish-to-start dependency [BE-S3-03]

   Task B's checkbox is disabled when its prerequisite (Task A) is
   not yet in completed status. Auto-unlock triggers after Task A
   completes, changing Task B from locked to ready."
   ```

   **Do NOT add `Co-Authored-By` trailers.** Commits are authored solely by the developer. No AI attribution lines.

7. **Repeat for the next logical commit** if the working tree still has unstaged changes from a different intent. Return to step 3.

8. **Verify the commits:**

   ```bash
   git log --oneline -5
   ```

9. **Report to the user:** commit hashes and messages for every commit you made.

## Checklist Before Done

- [ ] `bun run type-check` passed
- [ ] `bun test` passed
- [ ] `bun run lint` passed
- [ ] `bun run fmt` passed
- [ ] No `.env` files staged
- [ ] No `*.pem` key files staged
- [ ] Unrelated changes split into separate commits (one intent per commit)
- [ ] Commit message follows Conventional Commits format
- [ ] Scope matches the affected module
- [ ] Subject uses imperative mood
- [ ] Subject line is 80 characters or fewer (verified with `echo -n "..." | wc -c`)
- [ ] Every body line is 80 characters or fewer
- [ ] No `@<name>` or `@<digit>` anywhere in subject or body (use `v5` or backticks for version pins)
- [ ] Task ID referenced in subject when applicable

## Examples

```bash
# Good
feat(tasks): add dependency enforcement on task completion [BE-S3-03]
fix(auth): handle expired refresh token gracefully
test(projects): add service unit tests for template change [BE-S2-11]
chore(ci): add coverage threshold check to CI workflow
docs(onboarding): update setup steps for Docker dev environment
chore: bump demo CDN pin from v4 to v5

# Bad
update code
fix bug
WIP
added the task thing
chore: bump demo CDN pin from @4 to @5     # `@4`/`@5` become user mentions
fix: do thing and also bump version         # two intents — split into two commits
```
