---
name: ste100
description: Draft, revise, and audit English technical documentation using the prescriptive controlled-language workflow of ASD-STE100 Issue 9 (2025). Use for manuals, procedures, work instructions, descriptions, warnings, cautions, notes, specifications, and technical reviews. This skill orchestrates the standard and an approved project glossary; it does not replace the ASD dictionary or reproduce it.
---

# STE100 technical writing

Apply this skill when the requested output is technical English that must be clear for an international audience and controlled against ASD-STE100. Treat STE as constraints on writer behavior, not as a prompt for generic “simple writing.” Preserve technical accuracy, identifiers, quoted labels, units, requirements, and safety meaning.

## Authority, copyright, and trademark limits

Use ASD-STE100 Issue 9 (2025-01-15) as the governing source when it is available. The standard and its dictionary are copyrighted ASD material; possession of a copy is not itself a license. Use a dictionary copy only when the user or organization has lawful access, such as applicable special usage rights or written permission. See [dictionary/README.md](dictionary/README.md).

Do not extract, cache, publish, package, or reproduce ASD dictionary entries or examples in this skill, a repository, a database, or generated software. Do not generate an `approved-words.json` file from ASD. Keep only the interface to an externally supplied source and organization-owned glossary data. Treat “ASD-STE100 Simplified Technical English” as ASD's registered trademark; use the name for identification and attribution, not as a claim of ASD endorsement, certification, or affiliation.

Use the externally supplied official dictionary and the project's approved terminology database as authorities for word approval, part of speech, approved meaning, and verb forms. If they are unavailable, mark vocabulary findings as `UNVERIFIED`; do not invent an approval decision.

Do not copy or recreate Part 2's dictionary. Do not claim legal or certification compliance. Report `STE-aligned`, `STE findings unresolved`, or `STE audit passed` with the evidence and source issue used.

## Mandatory workflow

Read only the workflow and rule files needed for the requested document, then follow these stages in order:

1. Read [workflow/01-classify.md](workflow/01-classify.md). Classify every passage as procedural, descriptive, safety, note, quoted/literal, or mixed.
2. Read [workflow/02-plan.md](workflow/02-plan.md). Build a terminology ledger and identify applicable STE sections, source requirements, and unresolved terms.
3. Read [workflow/03-draft.md](workflow/03-draft.md). Draft with direct, unambiguous instructions and preserve the document's technical content.
4. Read [workflow/04-revise.md](workflow/04-revise.md). Revise in passes: meaning, classification, vocabulary, grammar, structure, safety, then mechanical checks.
5. Before delivery, read [audit/HOOK.md](audit/HOOK.md) and run the final gate. Read the relevant audit files; for a full review read all nine.

## Non-negotiable writing behavior

- Use approved dictionary words only with their approved part of speech, meaning, and forms. Use technical nouns and technical verbs only when their subject-field use is justified and recorded.
- Prefer the project's approved technical term. Do not alternate terms for one item. Keep newly selected technical nouns short and understandable; do not use regional slang or jargon.
- Keep multi-word nouns to three words when possible. Explain an unavoidable longer official term at first use, then use its approved short form or abbreviation. Never invent a shortening.
- Use only the infinitive, imperative, simple present, simple past, simple future, and permitted past participle as adjective. Avoid complex auxiliary constructions and progressive `-ing` forms except as allowed technical nouns or noun modifiers.
- Use active voice. In descriptive writing, retain passive voice only when the agent is genuinely unknown and making one up would change the technical meaning.
- Write short, complete sentences. Do not omit articles, subjects, verbs, or words; do not use contractions.
- Procedures use imperative commands, normally one instruction per sentence and no more than 20 words per sentence. Put prerequisite conditions before the command and separate them with a comma.
- Notes provide information only. Move instructions, limits, results, and safety controls out of notes and into the procedure or a correctly classified safety instruction. Notes may use up to 25 words per sentence.
- Make warnings and cautions direct. State the hazardous condition, the required or prohibited action, and the consequence when needed. Keep each safety sentence within the procedural limit.
- Preserve quoted text, placards, labels, identifiers, code, formulas, product names, and regulated wording as literals. Do not “STE-correct” them; annotate any conflict instead.
- Never use a semicolon; split into two sentences instead. Descriptive sentences may run up to 25 words (procedures stay at 20). Cap paragraphs at six sentences, each opening with a topic sentence.
- Apply the General Recommendations ([rules/general-recommendations.md](rules/general-recommendations.md)) as advisory guidance, not hard rules: keep "that" before subordinate clauses, disambiguate "with" and "this," avoid false friends and Latin abbreviations, use inclusive language (no gendered pronouns or "man"/"woman" outside a genuine contextual need), and use the possessive `'s` form cautiously.

## Deliverable contract

For a draft, return the document plus a short `Terminology and STE assumptions` section if approval data is incomplete. For a revision, provide the revised text and a compact change log for meaning-affecting changes, then re-run the audit gate before reporting it done. For an audit, report findings with severity per [audit/00-severity.md](audit/00-severity.md) (`BLOCKER`, `MAJOR`, `MINOR`, `UNVERIFIED`), location, rule, evidence, and proposed correction, and fill in [templates/audit-report.md](templates/audit-report.md) rather than only summarizing in chat. Never silently resolve an ambiguous technical meaning, downgrade a `BLOCKER` to reach a passing result, or report `STE audit passed` with an open `BLOCKER` or an unaccepted `MAJOR`/`UNVERIFIED` finding.

## Resource map

- Writing stages: [workflow/01-classify.md](workflow/01-classify.md) through [workflow/04-revise.md](workflow/04-revise.md)
- Rule orchestration: [rules/01-words.md](rules/01-words.md) through [rules/09-writing-practices.md](rules/09-writing-practices.md), plus [rules/general-recommendations.md](rules/general-recommendations.md) (GR-1 through GR-8, advisory)
- Exceptions and terminology: [rules/literals-and-identifiers.md](rules/literals-and-identifiers.md) and [rules/supplemental-reference-data.md](rules/supplemental-reference-data.md)
- Lawful dictionary integration: [dictionary/README.md](dictionary/README.md), [dictionary/adapter.md](dictionary/adapter.md), and [dictionary/company-terms.yaml](dictionary/company-terms.yaml)
- Audit gate: [audit/HOOK.md](audit/HOOK.md), severity rubric [audit/00-severity.md](audit/00-severity.md), [audit/01-source-fidelity.md](audit/01-source-fidelity.md) through [audit/09-final-gate.md](audit/09-final-gate.md), report template [templates/audit-report.md](templates/audit-report.md)
- Mechanical helper: `python3 scripts/audit_ste.py <file> [--procedural] [--json]`
