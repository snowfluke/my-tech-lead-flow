# Label set

Propose this set in Phase 1 step 3. `to-prd` and `to-issues` use the same labels.

Propose this default set (color is a suggestion):

- Type: `type:feature`, `type:bug`, `type:chore`, `type:refactor`, `type:docs`
- Area: `area:backend`, `area:frontend`, `area:infra` (one per role: `BE`, `FE`, `TL`/`DB`, from the Card ID prefix or the board's role column)
- Sprint: `sprint:0` ... `sprint:N`, one per sprint defined in `docs/business/sprint-breakdown.md` (do not invent sprint numbers; follow that file)
- Flow: `wiring` (frontend/backend integration cards), `blocked`, `needs-review`
- Source: `source:sit`, `source:uat` (bugs and requests from a test round; `triage` adds them), and `backlog` (moved out of the current release; no milestone)
- Priority (optional): `priority:high`, `priority:medium`, `priority:low`
