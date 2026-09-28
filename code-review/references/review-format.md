# Review body format

The shape `review_body.py check` enforces. `SKILL.md` step 7 links here.

## Example

````markdown
## Round 1 · Request Changes

**Gate:** `bun run complete-check` passes on the head (541 pass, 0 fail).
**CI:** Passes.

| ID | Finding | Severity | Status |
|----|---------|----------|--------|
| F1 | Guard rejects every Files adapter | BLOCKER | OPEN |

---

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

## Field rules

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

## Body rules

- The body is the skeleton and nothing else: header, Gate, CI, table, sections. Do not add praise, a summary, notes, or text after the last finding.
- A `---` line comes before every finding heading, with a blank line above it. It renders as a rule between findings.
- Every ask has an ID. If something needs action, it is a finding.
- A non-finding gets no line. Leave out "this is harmless" and "no action needed".
- Every sentence in Gate, CI, Problem, Question, Bug if, Fix and Done when has 20 words or fewer. The script counts them. Use active voice.
- Link every doc as an absolute URL pinned to `baseRefOid`: `https://github.com/<owner>/<repo>/blob/<baseRefOid>/<path>?plain=1#L<n>`. A `main` link drifts, and a relative link breaks on the Files tab.
- `·` appears only in the round header and the finding headings.
- No em dashes. No `--` outside code. No emoji.
