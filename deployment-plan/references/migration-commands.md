# Migration and seed commands

The rule in `SKILL.md` Writing rules, shown on one stack.

Good (a single command; the app finds its own files and config):

```bash
docker compose exec app <project migrate command>   # e.g. bun run db:migrate, ./manage.py migrate, migrate -path ... up
docker compose exec app <project seed command>
```

Bad (hardcoded path, inlined credentials, raw SQL, single file only): illustrated in TypeScript/Bun, but the anti-pattern is language-independent:

```bash
docker compose exec app bun -e "const {SQL}=require('bun');const fs=require('fs');
const db=new SQL('postgres://user:pass@10.0.0.1:5432/db');
await db.unsafe(fs.readFileSync('/app/src/db/migrations/0000_initial.sql','utf8'));"
```

If the only working command during an incident was the bad form, treat that as a deployment defect to fix in the image (ship a real migration runner behind a stable command), not as the runbook's recommended path.
