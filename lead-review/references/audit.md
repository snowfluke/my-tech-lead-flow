# Commit audit

Review commits that reached a branch without a PR: a range such as
`<from>..<to>` on `main`, or only one author's commits in that range. The
review format, severities, statuses, rounds, verifier, and check are the same
as for a PR. This file lists only what changes.

An audit blocks nothing: the code is already on the branch. Say so once to the
user when direct pushes are a habit, and suggest branch protection that
requires a PR.

## Range

`<to>` is the branch head unless the user names a commit. `<from>` is, in order:

1. The commit the user names.
2. The `<to>` of the last closed audit issue:

   ```bash
   gh issue list --state closed --search "Review: <branch> in:title" --limit 1 --json body --jq '.[0].body'
   ```

   Its `Range:` line holds `<from>..<to>`. Take the second SHA.
3. Otherwise, ask the user.

Resolve both to full 40-character SHAs with `git rev-parse`. With `--author`,
list the commits: `git log --author=<email> --format=%H --reverse <from>..<to>`.
If the list is empty, report that there is nothing to review and stop.

## Worktrees and diff (step 2)

```bash
git worktree add "/tmp/audit-<to7>-review<N>" <to>
git worktree add "/tmp/audit-<to7>-base<N>" <from>
git diff <from>..<to> > /tmp/audit-<to7>.diff
# With --author: that author's patches only, oldest first.
git show --format= $(git log --author=<email> --format=%H --reverse <from>..<to>) > /tmp/audit-<to7>.diff
```

Rules come from the `<from>` worktree, code from the `<to>` worktree. With
`--author`, other authors' commits are in the `<to>` worktree too: raise a
finding only on lines the author's patches add or change.

## Context (step 3)

- **Ledger.** The audit issue holds the rounds as comments. Round 1 has no issue yet. For a later round, save the last round:

  ```bash
  gh issue view <n> --json comments --jq '[.comments[] | select(.body | startswith("## Round"))] | last | .body // empty' > /tmp/audit-<to7>-prev.md
  ```

- **CI.** `gh run list --commit <to> --json name,conclusion`. Write the result on the CI line.
- **Base for links.** Pin rule links to `<from>`: pass it as `--base` in step 9.

## Review steps (step 5) that change

| Step | For an audit |
| --- | --- |
| 6. Acceptance criteria | Take the AC IDs from the commit messages: `git log --format=%B <from>..<to> > /tmp/audit-<to7>-body.md`. |
| 8. PR description | Skip. Check each commit message against its own diff instead. |
| 9. Scope | Check each commit against the card ID in its message. |
| 10. Mergeability | Skip. |

## Post (step 9)

Round 1 opens the issue. Put the range in the issue body, and the round in
the first comment, so every round is a comment in the same shape:

```bash
printf 'Range: %s..%s\nAuthor: %s\n' <from> <to> "<email or all>" > /tmp/audit-<to7>-issue.md
gh issue create --title "Review: <branch> <from7>..<to7>" --body-file /tmp/audit-<to7>-issue.md --label type:bug --assignee <author login>
gh issue comment <n> --body-file /tmp/audit-<to7>-review.md
```

Later rounds post a new comment with `gh issue comment`.

| Verdict | Issue |
| --- | --- |
| Request Changes | Stays open. |
| Approve | Close it: `gh issue close <n> --reason completed`. |

The author fixes the findings on a branch, with `address-review` and a normal
PR. That PR says `Refs #<n>`, never `Closes #<n>`: the issue closes only when
an audit round approves it.

## After posting (step 10)

Skip the draft, board, and sign-off steps. Remove the worktrees and the
`/tmp/audit-<to7>*` files.
