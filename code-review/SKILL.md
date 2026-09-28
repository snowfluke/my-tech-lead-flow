---
name: code-review
description: Act as a tech lead reviewing a pull request against the project's own coding standards and review checklist, in any language. Discovers the repo's standards docs, checks out the PR branch in an isolated git worktree, runs the project's test / lint / format / type-check gates, proves each finding, then posts a review in a fixed, script-checked format that stays identical across rounds. Use when the user asks to review a PR, review a branch, re-review a PR after changes, or do code review.
---

# Code Review

Review a PR as its tech lead. What backs a finding sets its severity:

| Severity | Backed by | Can the author argue? |
| --- | --- | --- |
| BLOCKER | Proof (a reproduction you ran, or a `file:line` trace), or a written project rule quoted verbatim | No |
| NIT | Neither. It is your preference. | Yes. The author may decline it with a reason. |
| QUESTION | A suspicion that only the author can settle | Not yet. The answer decides. |

Written rules are the checklist, the coding standard, `CLAUDE.md`/`AGENTS.md`, specs, ADRs, AC THEN clauses and the PR template. The script enforces the table: a finding with Rule or Proof must be a BLOCKER, and a NIT has neither. Never remove a Rule or Proof to lower a severity. A NIT you raise on PR after PR belongs in a written rule. Write the rule, or stop raising it.

Every review body has the same shape in every round. `scripts/review_body.py` builds the skeleton and checks the result. Do not post a body that the script rejects.

Paths in this file are relative to the directory that holds this `SKILL.md`. Find that directory first, then call each script by its absolute path, because the shell runs in the repo. Use `python3`. The scripts need only the standard library.

## 1. Read the project's standards

Read `README.md` first. Then read `CLAUDE.md` or `AGENTS.md` if present. Then find the standards. Look in the repo root, `docs/`, `.github/`, and `CONTRIBUTING.md`:

| Looking for | Common names |
| --- | --- |
| Coding standards | `CODING_STANDARD(S).md`, `STYLE_GUIDE.md`, `CONTRIBUTING.md`, `docs/coding-*.md` |
| Review checklist | `CODE_REVIEW_CHECKLIST.md`, `.github/PULL_REQUEST_TEMPLATE.md` |
| Architecture / specs | `docs/technical-specs/`, `ARCHITECTURE.md`, ADRs under `docs/adr/` |
| Stories / acceptance criteria | `docs/business/`, `USER_STORY.md`, `ACCEPTANCE_CRITERIA.md` |
| Task breakdown | `TASK_BREAKDOWN.md` |
| API specs | `docs/api-specs/`, `openapi.*` |

If no standards exist, raise behavior findings only.

## 2. Check out the PR in a worktree

The worktree keeps the user's checkout untouched.

```bash
git fetch origin
PR_BRANCH=$(gh pr view <number> --json headRefName --jq '.headRefName')
git worktree add "/tmp/pr<number>-review<N>" "origin/$PR_BRANCH"
```

Read PR source only from the worktree path. `gh pr diff|view|checks` work from anywhere. For a local branch with no PR, add a worktree for the branch and diff it against the base (`git diff <base>...<branch>`).

## 3. Gather context

```bash
gh pr view <number> --json title,body,author,baseRefName,baseRefOid,headRefOid,files,additions,deletions,commits,mergeable,mergeStateStatus
gh pr diff <number> > /tmp/pr<number>.diff
gh pr checks <number>
gh repo view --json nameWithOwner --jq .nameWithOwner
```

Step 9 needs `nameWithOwner` and `baseRefOid`.

Save the PR body to a file. Step 5 needs it:

```bash
gh pr view <number> --json body --jq .body > /tmp/pr<number>-body.md
```

Save the last posted round. It is the ledger for this round:

```bash
gh pr view <number> --json reviews --jq '[.reviews[] | select(.body | startswith("## Round"))] | last | .body // empty' > /tmp/pr<number>-prev.md
```

An empty file means this is Round 1.

## 4. Run the gates

Run the project's own gates in the worktree. Detect the toolchain. Do not assume `npm` or `bun`. Take the first match: a command documented in `CLAUDE.md`, README or `CONTRIBUTING.md`, then a manifest script, then the ecosystem default.

| Ecosystem | Detect via | Type-check · lint · format · test |
| --- | --- | --- |
| JS/TS | `package.json` and lockfile (`bun.lock` bun, `pnpm-lock` pnpm, `yarn.lock` yarn, else npm) | `<pm> run type-check` · `lint` · `fmt`/`format` · `test` |
| Rust | `Cargo.toml` | `cargo check` · `cargo clippy -- -D warnings` · `cargo fmt --check` · `cargo test` |
| Go | `go.mod` | `go vet ./...` · `golangci-lint run` · `gofmt -l .` · `go test ./...` |
| Python | `pyproject.toml`/`setup.cfg` | `mypy`/`pyright` · `ruff check` · `ruff format --check` · `pytest` |
| Java/Kotlin | `pom.xml`/`build.gradle` | `mvn verify` / `gradle build check` |

Prefer one aggregate script (`complete-check`, `ci`) if it exists. If a gate cannot run, say so on the Gate line. Do not report a pass you did not see.

## 5. Review

Do each step in order. Write each finding down as you find it.

1. **Checklist.** Print the walk skeleton: `python3 scripts/review_body.py walk <checklist> > /tmp/pr<number>-walk.md`. Give every line one verdict: `PASS`, `N/A`, `FAIL F<n>`, or `ASK F<n>`. Every `FAIL F<n>` is an OPEN BLOCKER whose Rule links that checklist line. Use `ASK F<n>` when only the author can tell, for example whether a manual smoke test ran. It points to an OPEN QUESTION. The script checks both directions. If the repo has no checklist, skip the walk and pass `--no-checklist` in step 9.
2. **Trace outside the diff.** For each changed function, middleware, route, config or type, grep its callers and the place it is registered or mounted. Many bugs sit where the changed code is used, not where it is written.
3. **Architecture.** Layering, module structure, file-size limits, duplicated utilities.
4. **Correctness and safety.** Error handling, input validation, auth, transactions, concurrency, secrets, injection.
5. **API contract.** If endpoints changed and specs exist, compare method, path, request, response, status and pagination with the spec.
6. **Acceptance criteria.** Skip this step if the PR cites no AC ID. Run `python3 scripts/check_ac_refs.py /tmp/pr<number>-body.md --business-dir docs/business`. A non-zero exit lists AC IDs that do not exist. For each cited AC, trace every THEN clause to the code. Match displayed text verbatim, in any language.
7. **Tests.** Each behavior and each cited AC has a test that fails when the behavior breaks.
8. **PR description.** Check each claim in the description against the diff. A claim the diff does not support is a finding. The diff or the changed-file list is its Proof.
9. **Scope.** If the PR cites a task card, compare each changed file with the card. List every unrelated file in one finding.
10. **Mergeability.** A PR that is not mergeable gets a BLOCKER: rebase on the base branch.
11. **CI.** A check that fails because of the PR is a BLOCKER. A check that also fails on the base branch is not a finding. Name it on the CI line and say which suites did not run.
12. **Prove it.** A BLOCKER needs Proof or a Rule. Without either, it is a NIT. If you suspect a bug and cannot prove it, check who can settle it. If only the author can (intent, a requirement, an external system), ask a QUESTION. If the code can, read the code. Otherwise do not post it.

## 6. Status and verdict

| Status | Set it when | Allowed for |
| --- | --- | --- |
| OPEN | You raise the finding | All |
| RESOLVED | Its Done when holds on the new head | BLOCKER, NIT |
| DECLINED | The author gave a reason in the PR thread, and you accept it | NIT |
| ANSWERED | The author answered in the PR thread | QUESTION |

Every status except OPEN is final. If an answer shows a bug, raise a new BLOCKER with a new ID. The QUESTION stays ANSWERED.

The verdict rule is the same in every round:

| State | Verdict |
| --- | --- |
| Any finding is OPEN | `--request-changes` |
| No finding is OPEN | `--approve` |

Nothing merges while a finding is OPEN, so no finding is forgotten. Never end on a plain `--comment`.

## 7. Write the body

Start from the skeleton. Do not write the body from memory.

```bash
# Round 1 (the prev file is empty):
python3 scripts/review_body.py next > /tmp/pr<number>-review.md
# Round 2 and later:
python3 scripts/review_body.py next /tmp/pr<number>-prev.md > /tmp/pr<number>-review.md
```

Fill every `{{...}}` placeholder. Write the file with a file-editing tool. Do not use a shell heredoc, because it breaks backticks. The finished body has this shape:

````markdown
## Round 1 · Request Changes

**Gate:** `bun run complete-check` passes on the head (541 pass, 0 fail).
**CI:** Passes.

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F1 | Guard rejects every Files adapter | BLOCKER | OPEN |

### F1 · Guard rejects every Files adapter · BLOCKER

**Where:** `src/data/data.router.ts:24`
**Problem:** The data guard also runs on storage routes. It throws `ENGINE_UNSUPPORTED` for every non-database adapter.
**Fix:** Make the guard check ownership only.

```diff
- adapterInProject(slug, id);
+ if (deps.adapters.byId(id)?.project_id !== projectOf(slug).id) throw notFound("adapter");
```

**Done when:** A test mounts data and storage together and a Files adapter reaches the storage handler.

<details><summary>Proof</summary>

```text
GET /projects/shop/adapters/a1/entries -> 422 ENGINE_UNSUPPORTED (storage handler never ran)
```

</details>
````

### Field rules

| Field | Rule |
| --- | --- |
| Heading | `### F<N> · <title> · <BLOCKER, NIT or QUESTION>`. The title has 12 words at most. Title and severity match the table row exactly. |
| Where | One of: `path:line` items separated by commas, commit `<sha>`, or `PR description: <part>`. |
| Problem | At most two sentences: what is wrong, and what it breaks. State the fault. Do not teach. |
| Rule | The written rule the diff breaks. Link it and quote it verbatim. Omit the line when no rule is broken; a rule you only cite as context goes in Proof. For an AC, quote the THEN clause, and say in Problem what the code shows instead. |
| Fix | One sentence, one approach. The approach may touch several files. It never offers a choice: the script rejects `or`, `either`, `alternatively` and `at minimum`. If you cannot pick one fix, ask the user before you post. |
| diff | One or more `diff` blocks after Fix. Several blocks are fine when one fix spans files. Show enough context lines to complete the changed statement. Use real values, never a stand-in such as `NNNN`. |
| Done when | One sentence the author can check: a test that passes, a command output, a line that is gone. |
| Proof | Only for what you ran or traced. Reproduction output, `file:line` traces and library internals go here. |
| Question | QUESTION only. At most two sentences. Ask what only the author knows. |
| Bug if | QUESTION only. One sentence: the answer that makes this a BLOCKER. If you cannot write it, do not ask. |

Each severity has its own fields, in this order:

| Severity | Fields |
| --- | --- |
| BLOCKER | Where, Problem, Rule, Fix, diff, Done when, Proof. It has Rule, Proof, or both. |
| NIT | Where, Problem, Fix, diff, Done when. No Rule, no Proof. |
| QUESTION | Where, Question, Bug if, then Proof if you have evidence. |

### Body rules

- The body is the skeleton and nothing else: header, Gate, CI, table, sections. Do not add praise, a summary, notes, or text after the last finding.
- Every ask has an ID. If something needs action, it is a finding.
- A non-finding gets no line. Leave out "this is harmless" and "no action needed".
- Every sentence in Gate, CI, Problem, Question, Bug if, Fix and Done when has 20 words or fewer. The script counts them. Use active voice.
- Link every doc as an absolute URL pinned to `baseRefOid`: `https://github.com/<owner>/<repo>/blob/<baseRefOid>/<path>?plain=1#L<n>`. A `main` link drifts, and a relative link breaks on the Files tab.
- `·` appears only in the round header and the finding headings.
- No em dashes. No `--` outside code. No emoji.

## 8. Later rounds

Round N copies Round N-1. It does not rewrite it. `review_body.py next <prev>` does the copy.

1. Keep every ID, title and severity. They are frozen.
2. Set each status by the table in section 6.
3. A status other than OPEN is final. File a regression or a new problem under a new ID.
4. Give a new finding the next free ID.
5. Keep a section for each OPEN finding. Edit only the fields that the new diff made wrong, usually Where.
6. Detail no closed finding.

## 9. Verify, check, then post

The script checks shape and the checklist walk. It cannot judge the other rule docs, or whether a Fix holds two asks. A verifier in a fresh context judges those.

1. Build the verifier prompt. Pass every rule doc you read in step 1:

   ```bash
   python3 scripts/review_body.py verify-prompt /tmp/pr<number>-review.md --diff /tmp/pr<number>.diff \
     --rules <checklist> <coding standard> <CLAUDE.md or AGENTS.md> <each spec a finding cites> > /tmp/pr<number>-verify-prompt.md
   ```

2. Run that prompt in a fresh context: a subagent if your harness has one, otherwise a new session. Never run it in the context that wrote the review. Save its output to `/tmp/pr<number>-verify.md`.
3. Run the check:

   ```bash
   python3 scripts/review_body.py check /tmp/pr<number>-review.md --repo <nameWithOwner> --base <baseRefOid> \
     --walk /tmp/pr<number>-walk.md --checklist <checklist> --verify /tmp/pr<number>-verify.md
   # No checklist in the repo: replace --walk and --checklist with --no-checklist.
   # Round 2 and later: add --prev /tmp/pr<number>-prev.md
   ```

4. Fix every error in the body. A verifier verdict other than `OK` is an error. Any change to the body makes the verification stale, so go back to 1. Two or three passes is normal: a verifier tends to catch one problem per pass.
5. If you judge a verdict wrong, do not edit the body to please it, and do not rerun until it passes. Append `F<n>: OVERRIDE <reason>` below the verifier's lines. Keep the verifier's line. Ask the user to approve each override: quote the verifier line and your reason. Post only after the user approves. The check prints every override as a warning.

Post only when the check prints `OK`.

```bash
gh pr review <number> --request-changes --body-file /tmp/pr<number>-review.md   # a finding is OPEN
gh pr review <number> --approve         --body-file /tmp/pr<number>-review.md   # nothing is OPEN
```

## 10. After posting

- If an OPEN BLOCKER exists and the project's flow expects it, convert the PR to draft: `gh pr ready <number> --undo`.
- Move the linked issue's board card to match the verdict. Run `gh pr view <number> --json closingIssuesReferences,projectItems`. If the PR links an issue on a board, set its `Status` with the board's own column names:
  - Request Changes: move it back to the in-progress column (for example `In Progress`).
  - Approve: move it toward done, per the board's convention. Many boards reach `Done` only on merge.

  Use `gh project item-edit --id <item-id> --field-id <status-field> --project-id <pid> --single-select-option-id <option>`. If no issue or board exists, skip this step. Never create a card.
- Fill in the PR template's reviewer sign-off, per project convention. Do not add a bot or an agent as a human reviewer.
- Remove the worktree and the temp files:

```bash
git worktree remove "/tmp/pr<number>-review<N>" --force
rm -f /tmp/pr<number>-review.md /tmp/pr<number>-prev.md /tmp/pr<number>-body.md /tmp/pr<number>.diff /tmp/pr<number>-walk.md /tmp/pr<number>-verify-prompt.md /tmp/pr<number>-verify.md
```
