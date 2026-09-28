# CLAUDE.md structure

`SKILL.md` step 2 writes `CLAUDE.md` in this order. Drop a section that does not
apply. It is an operating manual: terse, declarative, and dense with commands.

1. **Title and gate**: one line on what the project is, then one plain line naming the verification gate command to run before marking any task complete.
2. **Source of truth**: a pointer list mapping each concern to its authoritative doc (product to `docs/business/`, architecture to `docs/technical-specs/`, rules to `docs/coding-standard/`, work to `docs/task-breakdown/`, ops to `docs/deployment-plan/`, terms to `GLOSSARY.md`). The manual restates rules tersely; the docs hold the detail.
3. **Project overview**: a tech-stack table (layer to technology) and the repository layout tree with per-folder purpose.
4. **Boundaries**: the service/module map and any roles, domains, and state machines an agent must respect.
5. **Work model**: how cards are assigned, any scaffold/contract-stable model, who reviews.
6. **Architecture laws**: the hard rules, including the file-size cap and the split strategy, with the numbers from the coding standard (extract into a sibling submodule folder, keep the entry point thin), the module/feature file pattern, and layering (no business logic in handlers, data access only via the repository layer, no cross-module internal imports).
7. **Runtime do/don't**: a two-column table of the tools to use and the ones banned for this stack (e.g. the package manager, test runner, and forbidden alternatives).
8. **Verification gate**: the exact ordered commands to run before any task is considered complete.
9. **Code discovery protocol**: search before writing, read similar files, reuse utilities and types.
10. **Naming**: a table of element to pattern to example.
11. **Type safety, error handling, testing, database**: the terse rules restated from the coding standard.
12. **Git**: branch and PR flow, commit format, the trailer policy.
13. **Absolute prohibitions**: a table of violation to why, the things that must never appear in merged code.
14. **Context recovery checklist**: a checkbox list of the project-specific invariants to re-verify after compaction (the easy-to-forget specifics: ID formats, role names, state-machine transitions, hashing choices, naming quirks). This is what makes the manual resilient to lost context.
15. **Quick reference**: the everyday commands (dev, build, test, db, deploy) in one fenced block.
