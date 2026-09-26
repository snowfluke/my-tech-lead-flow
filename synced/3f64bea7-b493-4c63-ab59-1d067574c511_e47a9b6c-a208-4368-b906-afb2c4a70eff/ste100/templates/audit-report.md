# ASD-STE100 audit report

- Document:
- ASD source and issue:
- Dictionary/glossary and version:
- Mechanical scan: `python3 scripts/audit_ste.py ...` run on [date/commit], exit status [0/nonzero], all findings triaged: [yes/no]
- Reviewer/date:
- Gate re-run after last fix: [yes/no/n-a]
- Result: `STE audit passed` / `STE findings unresolved`

## Findings

Severity definitions: [audit/00-severity.md](../audit/00-severity.md). Every row must have a severity; an untriaged mechanical-scan hit is not a row yet — triage it first.

| Severity | Location | Rule | Evidence | Correction/status |
|---|---|---|---|---|
| [BLOCKER/MAJOR/MINOR/UNVERIFIED] | [file:line] | [STE section/rule] | [text] | [action] |

## Accepted exceptions

Only `MAJOR` and `UNVERIFIED` findings may appear here; `BLOCKER` findings have no exception path and must be fixed.

| Finding | Reason accepted | Approver | Date |
|---|---|---|---|

## Final gate

- [ ] Source fidelity checked ([audit/01-source-fidelity.md](../audit/01-source-fidelity.md)).
- [ ] Content classification checked ([audit/02-content-classification.md](../audit/02-content-classification.md)).
- [ ] Vocabulary checked against authoritative data, `UNVERIFIED` used where no source was available ([audit/03-vocabulary.md](../audit/03-vocabulary.md)).
- [ ] Grammar and sentence forms checked, including articles/demonstratives (rule 4.5) and applicable General Recommendations ([audit/04-grammar-and-sentences.md](../audit/04-grammar-and-sentences.md)).
- [ ] Procedures and descriptions checked, including paragraph rules and note validity ([audit/05-procedures-and-descriptions.md](../audit/05-procedures-and-descriptions.md)).
- [ ] Terminology ledger checked for one canonical term per item, no synonym drift ([audit/06-terminology.md](../audit/06-terminology.md)).
- [ ] Safety instructions checked, signal words matched to assessed risk ([audit/07-safety-instructions.md](../audit/07-safety-instructions.md)).
- [ ] Punctuation and word count checked, including the semicolon ban ([audit/08-punctuation-and-word-count.md](../audit/08-punctuation-and-word-count.md)).
- [ ] Mechanical scan findings all triaged (confirmed, reclassified, or dismissed with a stated reason).
- [ ] Accepted exceptions recorded with reason and approver; no open `BLOCKER`.
