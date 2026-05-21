---
name: us-ac-formatter
description: Convert user stories and acceptance criteria pasted as a markdown table into the project's Gherkin (Given/When/Then) format, grouped by sprint goal. Use when the user pastes a US/AC table and wants it reformatted into per-sprint Gherkin acceptance-criteria docs, or asks to "format these user stories", "turn this table into Gherkin", or "break these AC down by sprint".
---

<what-to-do>

The user gives you user stories and acceptance criteria as an ASCII or markdown table. Convert them into the project's structured output: `US-XX` story entries, `AC-XX.YY` Gherkin scenarios, and a sprint breakdown — matching the exact shape in `<output-format>`.

Steps:

1. **Parse the table.** Identify each user story (persona, action/goal, business value) and each acceptance criterion attached to it. One table row is usually one US or one AC; infer the columns from the header. If the table is ambiguous (columns unclear, AC not mapped to a US, no sprint hints), ask before guessing.

2. **Assign IDs.** Number stories `US-01`, `US-02`, … and their criteria `AC-<story>.<seq>` (`AC-01.01`). Preserve any IDs already present in the input rather than renumbering. If the input has gaps in numbering, keep them and add an inline `> Note:` like the existing docs do.

3. **Group by sprint goal.** Always ask the user for the sprint breakdown — which US belongs to which sprint, and each sprint's goal title — before emitting. Do not infer it from the table or invent one, even if the table has a sprint hint.

4. **Write Gherkin.** Convert each AC into a `Given / When / Then` body inside a ```gherkin fence. Use `And` for continuation lines, indented two spaces. Where a Then enumerates fields/buttons/options, list them as `  - item` bullets. Keep the user's domain wording and language verbatim (e.g. Bahasa Indonesia UI copy) — translate nothing.

5. **Emit the three artifacts** in `<output-format>`, writing them into the example docs structure (see `<file-targets>`). Read each target first if it exists; merge rather than clobber unless the user asks for a clean overwrite. Show a short summary of what was written.

</what-to-do>

<output-format>

### 1. User stories (`user-story.md` shape)

```
### US-01 — <Title>

- **Persona:** <persona>
- **Action:** <action/goal>
- **Business value:** <value>
```

### 2. Sprint breakdown (`sprint-breakdown.md` shape)

```
## Sprint 1 — <goal title>

1. US-01 — <Title> (<persona>)
2. US-02 — <Title> (<persona>)
```

### 3. Acceptance criteria, Gherkin per sprint (`acceptance-criteria-sprint-N.md` shape)

```
# Acceptance Criteria — Sprint 1

## User Stories in Scope

- **US-01** <Title> — <persona>

---

## US-01 — <Title> (<persona>)

### AC-01.01 — <scenario name>

​```gherkin
Given <precondition>
  And <more context>
When <action>
Then <expected outcome>
  - <enumerated field/option if any>
​```
```

</output-format>

<file-targets>

Write into the example `docs/business/` structure by default:

| Artifact | Path |
| --- | --- |
| User stories | `docs/business/user-story.md` |
| Sprint breakdown | `docs/business/sprint-breakdown.md` |
| AC Gherkin per sprint | `docs/business/acceptance-criteria-breakdown/acceptance-criteria-sprint-N.md` |
| AC index | `docs/business/acceptance-criteria.md` (the cross-sprint index/table — update the "Sprints at a Glance" table and per-sprint `AC-ID — Scenario` lists) |

Resolve paths relative to the repo root. If the working directory isn't the example repo or these paths don't exist, ask for the base path instead of creating a new tree. Keep the per-sprint AC bodies in the breakdown files and the one-line `AC-ID — Scenario` entries in the index, mirroring how the existing docs split full bodies from the index.

</file-targets>

<rules>

- Faithful conversion, not authoring. Do not add, remove, or reinterpret criteria — if an AC is vague, render it as-is and flag it in a trailing `> Note:` rather than fixing it (fixing is the `/grooming` skill's job).
- One scenario per AC. Don't merge or split rows.
- Preserve source language and exact domain terms/labels.
- Keep Gherkin steps in the canonical order: all `Given`/`And` context, then `When`, then `Then`. Multiple whens/thens use `And`.

</rules>

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
