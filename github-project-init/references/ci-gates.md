# CI gates

Three gates. The PR gate gives the author feedback. The branch gate catches a
broken merge result fast. The build gate tests the exact commit that ships.

| Gate | Trigger | Runs | Command |
| --- | --- | --- | --- |
| PR (heavy) | `pull_request` | Type-check, lint, format, unit and integration tests, build, the e2e specs the PR affects, and the `pr-hygiene` job | The aggregate check command, then `test:e2e` for the affected specs |
| Branch (light) | `push` to `dev`, `test`, `main` | Type-check, lint, and the fast unit tests | `check:fast` |
| Build (heavy) | `workflow_dispatch` and `release: published`, in `build.yml` | The aggregate check command and the full e2e suite, heavy-tagged scenarios included, before the image or artifact is built | The aggregate check command, then `test:e2e:full` |

The PR gate is the required status check. Name its jobs once and keep the
names: branch protection matches checks by name, and a renamed check blocks
every merge.

## The condition

The split saves minutes only when builds are rarer than merges. Ask the user
whether any environment deploys on every merge.

- **No** (builds run by dispatch or on release): use the three gates.
- **Yes:** the build gate runs on every merge, so it replaces the branch gate for that branch. Run the build gate on that branch, and keep the branch gate on the others.

Also ask whether every change reaches `dev` through a PR. If people push
straight to a long-lived branch, the branch gate is the only check that code
gets before the build. Then run the PR gate's commands on that push instead,
and recommend branch protection that requires a PR.

## Defaults on every workflow

- **Cancel stale runs.** Key `concurrency` on the workflow and the PR number or the ref, with `cancel-in-progress: true`. A new push to a PR stops the run for the old push. Do not cancel runs of `build.yml`: a cancelled deploy can leave an environment half updated.
- **Timeouts.** Set `timeout-minutes` on every job, a little above its normal run time. A hung job otherwise runs for 6 hours.
- **Dependency cache.** Turn on the setup action's cache, keyed on the lockfile, for example `cache: npm` in `actions/setup-node`. For Bun, cache `~/.bun/install/cache` with `actions/cache`.
- **Docs-only changes.** Add `paths-ignore` for `docs/**` and `**/*.md` to the PR gate. If the PR gate is a required check, a skipped workflow leaves the check pending and blocks the merge. In that case, do not use `paths-ignore`. Add a first job that detects a docs-only change, and make every heavy job skip on its output, so the required check still reports.

Write a one-line comment in the workflow above each default that says why, so
the next person does not undo it.
