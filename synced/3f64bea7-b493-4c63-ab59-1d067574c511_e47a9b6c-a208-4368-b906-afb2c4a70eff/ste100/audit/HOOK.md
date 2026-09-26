# Audit hook

Run this gate before presenting a document as complete, after any material revision, and again after every fix applied in response to a prior finding. A gate run that follows a fix is not optional — a corrected sentence can introduce a new violation the original pass never covered.

```bash
python3 scripts/audit_ste.py path/to/document.md --procedural
```

The script is a mechanical triage tool, not a certification, and it does not inspect the ASD dictionary or make severity determinations on its own (see [audit/00-severity.md](00-severity.md)). Its exit code only tells you whether mechanical findings exist, not whether the document is STE-aligned. A zero exit status is necessary but never sufficient — it does not substitute for the human/agent audit files. A non-zero exit status does not by itself block anything; each finding must be triaged (confirmed, reclassified, or dismissed as a false positive with a stated reason) before it counts toward the gate.

Read [audit/00-severity.md](00-severity.md) first, then perform the numbered human/agent audit files (01 through 09) in order. Read all nine for a full review; for a scoped revision, still read 09 and any file whose subject the revision touched.

Fail closed: if the lawful ASD dictionary source, the project glossary, or a rule/audit file this gate depends on is unavailable or unreadable, stop and report the gap — do not proceed as if the check passed. A gate that cannot run a check is not the same as a gate that passed it.

A final pass requires all of:

- no unresolved `BLOCKER` finding, anywhere, with no exception process available for `BLOCKER` — it must be fixed and the gate re-run;
- no unresolved `MAJOR` finding, or each is recorded as an explicit accepted exception with reason and approver;
- no `UNVERIFIED` finding, or each is recorded as an explicit accepted exception with reason and approver;
- every mechanical-scan finding triaged (confirmed with a severity, reclassified, or dismissed as a false positive/literal with a stated reason) — an untriaged script finding blocks the gate the same as a confirmed one;
- source fidelity confirmed against the original;
- all safety content classified and placed correctly, with signal words matched to actual assessed risk;
- terminology ledger complete for every controlled term, with no unresolved synonym drift;
- external dictionary access confirmed lawful, when used, and its source/version recorded;
- the audit report ([templates/audit-report.md](../templates/audit-report.md)) filled in and saved alongside the reviewed document, not only stated in chat.

Report `STE audit passed` only when every item above is satisfied. Report `STE findings unresolved` otherwise, and list what remains open. Never report `STE audit passed` because a deadline is close or because re-running the gate is inconvenient.

For a repository hook, call the script only for changed technical documents and pass the project's approved glossary/dictionary through the surrounding CI job. Never rewrite files automatically in a hook, and never suppress or filter script findings before a human/agent reviewer sees them.
