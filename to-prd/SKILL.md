---
name: to-prd
description: Add a feature or change request to a project that is already running. Turns the latest grill-me decision log, or the conversation, into new user stories and Gherkin acceptance criteria in docs/business/ in us-ac-formatter's format, continuing the US and AC numbering. Asks only for what the acceptance criteria need and the input lacks, lists the specs the change touches, and opens a parent GitHub issue that links it all. Use when the user wants a PRD, wants to add a feature mid-project, or asks to turn a discussion into stories. Hands off to to-issues.
---

# To PRD

The mid-project entry to the pipeline. `product-discovery` and `us-ac-formatter`
start a project. This skill adds to one that already runs, in the same format,
so `docs/business/` stays the single source of truth.

## 1. Read the input and the project

- **Input.** Take the latest decision log in `docs/decisions/`, if `grill-me` wrote one for this feature. Otherwise use the conversation.
- **Business docs.** Read `docs/business/user-story.md`, `sprint-breakdown.md`, and the per-sprint files under `acceptance-criteria-breakdown/`. Note the highest US number and the sprints that exist.
- **Glossary.** Read `docs/GLOSSARY.md` if it exists, and use its terms.
- **Specs.** Read `docs/technical-specs/_index.md` and `docs/api-specs/_index.md` if they exist.

If `docs/business/` does not exist, check whether the project has code.

- **Running project (adopt mode).** Create the skeleton in `us-ac-formatter`'s file targets: `user-story.md`, `sprint-breakdown.md`, and `acceptance-criteria-breakdown/` with the first sprint file. Start at `US-01`. Features that already shipped get no stories.
- **No code yet.** This is a new project. Stop and point the user at `product-discovery`.

## 2. Draft the stories and criteria

- One `US-XX` per actor goal, numbered from the next free number, with persona, action, and business value.
- One `AC-XX.YY` per observable outcome, as a Gherkin scenario.
- Keep the user's wording and UI language verbatim. Translate nothing.

## 3. Ask about the gaps

Ask only what a THEN clause needs and the input does not give: the exact message
or label text, the role that may act, and the empty, error, and loading states.
Ask which sprint the stories belong to. Never guess a sprint.

Ask one question at a time, each with a recommended answer, the way `grill-me`
does. Then show the full draft and get the user's approval.

## 4. Write the business docs

Read the `us-ac-formatter` skill's `references/layout.md` and follow its output
format and file targets exactly. Merge into the existing files. Do not rewrite stories
or criteria that are already there. Then regenerate the AC index with that
skill's script:

```bash
python3 <us-ac-formatter dir>/scripts/build_ac_index.py --business-dir docs/business --write
```

Hand the changed files to `git-commit`. The parent issue links to them, so the
user pushes before step 6.

## 5. List the spec impact

Name each section in `docs/technical-specs/` and `docs/api-specs/` that the
change touches, and say what must change there in one line each. Do not edit
the specs here. `technical-spec` and `api-spec` own them.

## 6. Open the parent issue

Show the issue to the user and create it only after they approve:

```bash
gh issue create --title "US-XX <feature name>" --body-file /tmp/prd-<slug>.md --label type:feature --label sprint:<n> --milestone "<sprint milestone>"
```

Use the labels and milestones that `github-project-init` created. If one is
missing, ask. Do not create a new label. The body follows [references/parent-issue.md](references/parent-issue.md).

Report the issue number. The next step is `to-issues` with that number.
