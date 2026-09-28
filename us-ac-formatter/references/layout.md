# Business docs layout

The output shape (`SKILL.md` step 5) and where each file goes.

## Output format

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

## File targets

Write into `docs/business/` by default:

| Artifact | Path |
| --- | --- |
| User stories | `docs/business/user-story.md` |
| Sprint breakdown | `docs/business/sprint-breakdown.md` |
| AC Gherkin per sprint | `docs/business/acceptance-criteria-breakdown/acceptance-criteria-sprint-N.md` |
| AC index | `docs/business/acceptance-criteria.md` (the cross-sprint index/table; update the "Sprints at a Glance" table and per-sprint `AC-ID — Scenario` lists) |

Resolve paths relative to the repo root. If `docs/business/` does not exist, create it with these files. Ask for another base path only when the project already keeps its docs under a different root. Keep the per-sprint AC bodies in the breakdown files and the one-line `AC-ID — Scenario` entries in the index, mirroring how the existing docs split full bodies from the index.
