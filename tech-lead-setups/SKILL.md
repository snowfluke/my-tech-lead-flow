---
name: tech-lead-setups
description: Scaffold a new project as the Tech Lead would in Sprint 0, after the task breakdown and before coding standards are written. Grills on folder structure, architectural patterns, commit hooks, tooling, and stubs, then executes the scaffold: directory layout, tooling config, pre-commit hooks, and endpoint/page stubs that return mock responses so frontend and backend can build in parallel from day one. Use when the user wants to set up, bootstrap, or scaffold a project, stand up the repo skeleton, do Sprint 0, or asks to "set up the project".
---

# Tech Lead Setup

Stand up the project skeleton so every developer can start their first card without blocking anyone. This is the Sprint 0 scaffold: structure, tooling, hooks, and stubs, executed from the decisions already made upstream.

This runs **after** `task-breakdown` (the cards, including any Sprint 0 scaffold cards, exist) and **before** `coding-standard` (the standards describe the skeleton this skill creates). Two phases: **grill to lock the setup, then execute it.**

## Phase 1 — Grill

**Read `docs/technical-specs/` first; it is the source of truth for this scaffold.** The repository structure, tech stack, module definitions, and environment configuration are already decided there: read `03-repository-structure.md` for the directory tree, `04-tech-stack.md` for the runtime/tooling/versions, `05-module-definitions.md` for the per-module surface, and `11-environment-configuration.md` for the env vars. Also read the Sprint 0 cards in `docs/TASK_BREAKDOWN.md`, the endpoint contracts in `docs/api-specs/`, and any conventions in `CLAUDE.md`. Pull every decision you can from these and confirm it rather than re-deciding; the grill only fills genuine gaps. If `docs/technical-specs/` does not exist, say so and run `technical-spec` first, because scaffolding without it means inventing architecture the rest of the pipeline has not agreed to.

Interview the user one question at a time, recommending an answer each, until the setup is fully pinned:

- **Folder structure.** Monorepo vs polyrepo, workspace layout, where app code, shared code, modules/features, tests, scripts, and docs live. The exact tree to create.
- **Patterns.** The per-module / per-feature file pattern the scaffold must reproduce (e.g. backend module = route + service + repository + schema + test per endpoint; frontend feature = model + presenter + view). A new file should be obvious to place.
- **Commit hooks.** What runs pre-commit (format, lint, type-check, tests on staged files), and the hook tool. Defer to the `setup-pre-commit` skill for the mechanics. Offer the `git-guardrails-claude-code` hook if the user wants destructive-command protection.
- **Tooling.** Package manager and lockfile, type-checker, linter, formatter, test runner, build, and the CI workflow. The exact `scripts` entries and an aggregate check command (e.g. `complete-check`).
- **Stubs.** Which endpoints and pages to scaffold and the mock-response shape. The point of stubs: a stub returns a contract-valid hardcoded response (matching `docs/api-specs/` where present) so frontend integrates against it from day one and no one is blocked. Confirm the stub depth (mock response only, vs real health probes, etc.).

Surface contradictions against the specs ("the tech-stack doc says Bun but there's a `package-lock.json` here, which wins?") and flag anything underspecified before creating files. When the setup is locked, summarize what you will create and confirm before executing.

## Phase 2 — Execute

Create the scaffold for real. Group the work and report what you create.

1. **Initialize** the project with the chosen package manager; write the manifest, lockfile, and `scripts` entries.
2. **Create the directory tree** exactly as agreed, with a placeholder or index file in each directory so the structure is committable and navigable.
3. **Write tooling config** for the type-checker, linter, formatter, and the CI workflow. Pin versions.
4. **Install commit hooks** via the `setup-pre-commit` skill so format/lint/type-check/test run on staged files. Add the guardrail hook if requested.
5. **Scaffold stubs**: one stub per endpoint following the module pattern, each returning a contract-valid mock response (typed mock constants, matching `docs/api-specs/`), plus page/route placeholders that link the relevant pages per role. Real probe code only where it must be live (e.g. health checks).
6. **Generate shared types/constants** if the structure has a shared package.

## Verify

Run the project's own gate end to end and confirm a clean baseline before handing off:

```
<type-check> && <lint> && <format-check> && <test> && <build>
```

Use the exact commands established in the grill. The scaffold must pass green on an empty project: stubs compile, mock responses satisfy their contracts, hooks fire, CI is valid. Report the result. If a gate cannot run here (missing runtime), say so explicitly rather than claiming a pass.

## Notes

- Composes with `setup-pre-commit` (hooks) and `git-guardrails-claude-code` (destructive-command protection); invoke them rather than re-implementing.
- The scaffold is the thing `coding-standard` then describes and `code-review` enforces, so keep the patterns consistent with what those skills will document.

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
