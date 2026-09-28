# Orientation docs layout

`README.md` and `GLOSSARY.md` stay single files. The two guides are folders
with one file per section.

```text
README.md                         repository root
docs/GLOSSARY.md
docs/development-guide/
  _index.md                       who it is for, table of contents
  01-day-one-setup.md
  02-work-model.md                the work split and the sprint model
  03-<card kind>.md               one file per kind of card, for example 03-backend-card.md
  04-<card kind>.md
  05-review-a-pull-request.md
  06-release.md
docs/onboarding/
  _index.md                       who it is for, table of contents
  01-project-context.md
  02-prerequisites.md
  03-local-setup.md
  04-codebase-walkthrough.md
  05-workflow.md
  06-key-concepts.md
  07-getting-help.md
```

Leave out a section the project does not need and keep the numbering
contiguous.

## README.md
The front door, kept lean. What the project is and the problem it solves; key tech/stack; a quickstart (prerequisites → install → run → test) that actually works; a high-level repo-structure map; and links out to the deeper docs (onboarding, glossary, standards, deployment) rather than inlining them. Badges/license/contributing pointer if the project uses them.

## GLOSSARY.md
A pure glossary: definitions only, no implementation detail. Group terms by domain area (e.g. domain entities, lifecycle/status, actions/buttons, roles). Each entry: the canonical term, its UI label if different (quote non-English labels verbatim), and a one-to-two-sentence definition. Disambiguate overloaded words ("account = Customer, not User"). Pull terms from real usage; don't invent vocabulary the project doesn't use.

## Development guide

Concrete, role-based walkthroughs of the recurring jobs, start to finish, one
file per scenario. Each scenario is an ordered, runnable sequence of steps with
the exact commands, and names the relevant skill or doc at each step (for
example "run the verification gate per the coding standard", "review per the
checklist"). This is the "how we work here" doc.

## Onboarding guide

The newcomer's path, one file per step, in order: project context (what and
why, the domain in a paragraph); prerequisites (tools and versions); local
setup (automated path and manual fallback, both verified); a codebase
walkthrough (the map plus what to read first); the development workflow in
brief (linking the development guide); key concepts (linking the glossary); and
where to get help. It gets a new contributor to a green local build and a first
change.

## Older projects

An older project may have `DEVELOPMENT_SCENARIO_GUIDE.md` and
`ONBOARDING_GUIDE.md` as single files. To migrate, move each section into its
numbered file and fix every link that pointed into the old file.
