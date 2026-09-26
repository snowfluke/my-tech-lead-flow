# STE100 technical writing skill

[![skills.sh](https://img.shields.io/badge/skills.sh-ste100-black?logo=vercel)](https://skills.sh)

An agent skill for drafting, revising, and auditing English technical documentation using the controlled-language writing rules of ASD-STE100 (Simplified Technical English). It gives an AI coding/writing agent a workflow, a set of rule summaries, and an audit gate — it does not include, replace, or substitute for the ASD-STE100 standard itself.

## Installation & Discovery

Install this skill using the [`skills`](https://skills.sh) CLI:

```bash
npx skills add amaruki/ste100
```

## What this repository is

- A structured workflow (`workflow/`) for classifying, planning, drafting, and revising technical text.
- Original, paraphrased summaries of the ASD-STE100 Issue 9 (2025) writing rules (`rules/`), written in this project's own words for orchestration purposes.
- An audit process and severity rubric (`audit/`) plus a mechanical triage script (`scripts/audit_ste.py`) for catching common, checkable issues (word-count limits, banned constructions, semicolons, contractions, and similar).
- Templates (`templates/`) and an interface contract for connecting a lawfully obtained ASD-STE100 dictionary or an organization's own terminology data (`dictionary/`).

## What this repository is not

- It is **not** ASD-STE100 itself, and it does not contain the ASD-STE100 Part 2 dictionary or any bulk extract of it. See [dictionary/README.md](dictionary/README.md).
- It does **not** certify, guarantee, or warrant that any document produced or reviewed with this skill conforms to ASD-STE100, meets any airworthiness, regulatory, contractual, or safety requirement, or is fit for publication without independent human review.
- It is **not** produced, reviewed, or endorsed by the Aerospace, Security and Defence Industries Association of Europe (ASD), and it makes no claim of affiliation, sponsorship, or certification by ASD. "ASD-STE100" and "Simplified Technical English" are used here solely to identify the referenced standard.
- It is **not** legal advice. Questions about licensing, permitted use, or reproduction of ASD-STE100 should go to ASD or to qualified counsel, not to this repository.

## Using this skill

1. Obtain lawful access to an ASD-STE100 Issue 9 dictionary source yourself, or supply your organization's own approved terminology data — see [dictionary/README.md](dictionary/README.md) and [dictionary/adapter.md](dictionary/adapter.md). This skill does not supply, cache, or infer dictionary approval on its own; without a lawful source, vocabulary findings are marked `UNVERIFIED`, not approved.
2. Start from [SKILL.md](SKILL.md) for the governing instructions, the writing workflow in [workflow/](workflow/), and the rule summaries in [rules/](rules/).
3. Before treating any document as finished, run the audit gate — [audit/HOOK.md](audit/HOOK.md), the severity rubric in [audit/00-severity.md](audit/00-severity.md), and `scripts/audit_ste.py` for the mechanical pass. Findings require human/agent review; the script alone is a triage aid, not a pass/fail authority.

## Copyright and trademark

ASD-STE100 Simplified Technical English, including its writing rules and Part 2 dictionary, is copyrighted by the Aerospace, Security and Defence Industries Association of Europe (ASD), and "ASD-STE100 Simplified Technical English" is ASD's registered trademark. Per ASD's own copyright notice, receiving or possessing a copy of the standard does not by itself grant a license to reproduce or publish it, and special usage rights are limited to specific categories of organizations defined by ASD.

This repository does not reproduce ASD-STE100's writing-rule text, dictionary entries, or examples. The material in `rules/` is this project's own original paraphrase, written for the purpose of directing an AI agent's behavior, and is not a substitute for the standard itself. Anyone who needs the authoritative rule text or dictionary should obtain it directly from ASD or the ASD-STE100 Maintenance Group (see `dictionary/README.md` for the relevant citation).

## License

The original content of this repository — the skill instructions, workflow and audit files, rule summaries, templates, and scripts — is released under the [MIT License](LICENSE).

This license applies only to that original content. It does not apply to, and confers no rights in, ASD-STE100 or its dictionary, which remain the property of ASD under its own copyright and trademark terms noted above.

## Disclaimer

This software and its content are provided "as is," without warranty of any kind, express or implied, including without limitation warranties of accuracy, merchantability, fitness for a particular purpose, or non-infringement. Use of this skill is at your own risk. The authors and contributors are not liable for any claim, damages, or other liability arising from the use of this repository, including any document drafted, revised, or audited with it. Always have technical, safety-critical, and regulatory content independently reviewed by a qualified human before publication or use.

## Reporting a problem

This repository is maintained in good faith to avoid reproducing ASD-STE100's copyrighted or trademarked material and to avoid infringing any other party's rights. If you are a rights holder, or anyone else, and believe any file in this repository infringes a copyright or trademark, discloses information it should not, or otherwise needs to be corrected or removed, contact **krilinamar@gmail.com** with the specific file and concern, and it will be addressed promptly, including removal if warranted.
