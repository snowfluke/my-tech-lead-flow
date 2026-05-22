---
name: task-breakdown
description: Act as the Tech Lead and break a set of user stories + acceptance criteria into a sprint-by-sprint, role-assigned task board in the project's TASK_BREAKDOWN.md format. Reads docs/business first, asks for team size and roles, splits work into Backend/Frontend cards, and — critically — makes frontend↔backend wiring its own explicitly-owned card. Use when the user wants to break work into sprint cards, plan a sprint board, assign tasks to engineers, or asks to "break this down into tasks".
---

<what-to-do>

You are the Tech Lead at sprint planning. Turn user stories and acceptance criteria into a pre-assigned task board, card by card, in the format shown in `<output-format>`.

This board is **engineering work**: backend, frontend, and Tech-Lead scaffold/infra cards. Deployment, release, and ops procedures are not cards here; they belong in `DEPLOYMENT_PLAN.md`. Sprint numbers and goals follow `docs/business/sprint-breakdown.md`; do not invent your own.

**Grill before planning.** Owner assignment and sequencing are downstream of decisions the docs don't record. After gathering the source (step 1), grill the user one question at a time — recommending a default and the trade-off for each — until the team shape, per-sprint scope, and card-granularity expectations are settled. Don't write a card until they are.

1. **Gather the source of truth.** Read `docs/business/` first — `user-story.md`, `acceptance-criteria.md`, and the per-sprint bodies under `acceptance-criteria-breakdown/`, plus `sprint-breakdown.md` if present. Pull sprint goals, US, and AC IDs from there. Also skim `docs/technical-specs/` and `docs/api-specs/` to cite authoritative Docs sections per card. If those paths don't exist, ask for the source rather than inventing stories.

2. **Establish the team (grill).** Grill the user on how many engineers and their roles (e.g. 1 Backend, 2 Frontend, 1 Tech Lead) unless they already stated it or `docs/TASK_BREAKDOWN.md` records an existing composition. Map each role to a name placeholder (`BE1`, `FE1`, `FE2`, `TL`). The team shape drives owner assignment and load-balancing, so resolve it before any card is written.

3. **Break each sprint into cards.** For every sprint goal, split the work along the Backend / Frontend dichotomy. One card = one shippable, independently-verifiable slice owned by one person. Give each a `Card ID` (`<BE|FE|TL|DB>-S<sprint>-<NN>`), a PM Card Title (one action-oriented line), a Task Description, the AC IDs it satisfies, an Owner, an Est in developer-days, and the authoritative Docs sections. Sequence cards so backend contracts and frontend shells exist before the work that depends on them.

4. **Make wiring an explicit card — the core job of this skill.** See `<wiring-cards>`.

5. **Balance and total.** Spread cards across same-role engineers so no one is idle. Close with a Definition of Done block and a per-sprint summary table (cards and est per role), matching the existing doc.

6. **Write the board to `docs/TASK_BREAKDOWN.md`** (create or edit in place — see `<rules>`), then report what changed.

</what-to-do>

<wiring-cards>

The recurring failure this skill exists to fix: a feature's backend card and frontend card both exist, but the **integration** — pointing the real frontend at the real backend, replacing the mock/scaffold, handling the live error envelope, verifying the AC end-to-end against the running server — belongs to no card and no one owns it. It falls through the gap and the AC is never actually proven.

For every feature where backend and frontend are separate cards, decide whether the seam between them needs its own wiring card. Create one when integration is non-trivial: contract mismatch risk, real error/empty/loading states to map, auth/permission interplay, or an end-to-end AC that only passes once both sides are live.

Ownership rule — **assign the wiring card to whoever owns the last task that unblocks it.** Walk the dependency chain for that feature; the wiring card depends on both the BE and FE cards, so its owner is the owner of whichever of those finishes last (the one that was blocking integration). If the backend lands last, backend owns the wiring; if the frontend view is the final piece, frontend owns it. State the unblocking card in the Task Description (e.g. "Depends on BE-S2-05 and FE-S2-08; BE-S2-05 lands last, so BE owns the wiring").

A wiring card is real work: give it a Card ID (you may use a `-WIRE` style title or just the next `NN`), an Est, the AC IDs it actually proves end-to-end, and a Docs reference. Prefer to attach an e2e check (e.g. an `add-maestro-flow` flow) that proves the AC against the running dev server as the card's exit criterion.

</wiring-cards>

<output-format>

Mirror `docs/TASK_BREAKDOWN.md` exactly:

- A header per sprint: `## Sprint N: <name>`, then `Stories: US-…`, then `Goal: …`.
- `### Backend` and `### Frontend` subsections, each a markdown table with columns: `Card ID | PM Card Title | Task Description | AC | Owner | Est | Docs`.
- Wiring cards live in the Backend or Frontend table according to the ownership rule above (not a separate section), so the owning engineer sees it in their lane.
- A `## Definition of Done (per card)` block.
- A `## Summary` table: `Sprint | Focus | BE cards | FE cards | BE Est | FE Est`.

Card IDs: `<BE|FE|TL|DB>-S<sprint>-<NN>`, zero-padded NN, sequential within role+sprint. Preserve any existing IDs when updating an existing board.

</output-format>

<rules>

- Tech Lead judgement, grounded in the docs — never invent AC or stories. Every card cites real AC IDs from `docs/business/`; if an AC is missing for work you think is needed, flag it (point the user at `/grooming`) rather than fabricating one.
- One owner per card. Estimates in developer-days, sized so a card fits comfortably within a sprint; split anything that doesn't.
- Respect an existing scaffold/work model if the repo documents one (e.g. Terral's Sprint-0 Tech-Lead scaffold + API-contract-stable model) — don't re-plan Sprint 0 unless asked.
- Write the result to `docs/TASK_BREAKDOWN.md` — this skill produces a file, not just chat output. If the file exists, read it first and **edit in place**: add or update only the affected sprint sections and refresh the Summary table, preserving Sprint 0 and any sprints/cards you weren't asked to change. If it doesn't exist, create it (with the How-to-Use header, engineer composition, work model, sprint sections, DoD, and Summary). If `docs/` isn't the current repo, ask for the target path before writing. After writing, report which cards were added/changed.

</rules>

## Helper scripts

After writing or editing the card tables, do **not** hand-count the Summary
table. Regenerate it deterministically and validate Card IDs:

```bash
python scripts/recompute_summary.py docs/TASK_BREAKDOWN.md --write
```

It recomputes BE/FE card counts and Est sums per sprint, rewrites the `## Summary`
section in place, and exits non-zero (with warnings) on duplicate or
non-sequential Card IDs. Run without `--write` to preview.

Then verify every cited AC actually exists in the business docs:

```bash
python scripts/check_ac_refs.py docs/TASK_BREAKDOWN.md --business-dir docs/business
```

Non-zero exit means a card cites a fabricated or stale AC ID; fix it before
finishing (or flag the missing AC via `/grooming`).

## Writing conventions (enforced in all output)

- No AI slop: no filler or hedging; every sentence informs. Use the `stop-slop` skill on prose when unsure.
- No em-dashes, no double-dashes (`--`) in prose; dashes only as Markdown syntax (list bullets, table rules) or in literal code/CLI flags (e.g. `--no-deps`).
- No emoji. Professional, declarative tone.
- If a document carries a metadata header (`**Version:**`, `**Date:**`, `**Author:**`, `**Status:**`, `**Phase:**`), each such line ends with two trailing spaces so Markdown renders them on separate lines.
