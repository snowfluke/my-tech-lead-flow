# Supplemental reference data

The skill needs externally supplied or project-local data to make vocabulary decisions. Prefer, in order:

1. A lawfully supplied ASD-STE100 Issue 9 dictionary, accessed through the interface in `dictionary/adapter.md`.
2. Company/industry/subject-field glossary and terminology database.
3. Publication specification, customer style guide, and approved abbreviations.
4. Source document's literal and regulatory text.

Record each source and version. Do not infer that a word is approved because it sounds simple or appears in an example. When sources conflict, preserve technical meaning, follow the higher-priority directive, and report the conflict.

Never commit ASD dictionary contents, bulk extracts, search indexes, or generated word lists. Commit only organization-owned terms and configuration that tells the audit process where an authorized external source is available.
