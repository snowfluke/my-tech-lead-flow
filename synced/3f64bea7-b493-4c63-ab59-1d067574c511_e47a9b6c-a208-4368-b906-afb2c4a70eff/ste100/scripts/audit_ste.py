#!/usr/bin/env python3
"""Deterministic triage checks for ASD-STE100-oriented technical prose.

This tool deliberately does not decide dictionary approval, and it does not assign
final severities. Every finding here is a candidate for human/agent triage against
audit/00-severity.md and the applicable rule file before it counts toward the audit
gate (audit/HOOK.md). Use a lawfully supplied external ASD source and the project
terminology ledger for dictionary-approval decisions this script cannot make.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Note: a bare "word's" is deliberately NOT flagged as a contraction — it is far more
# often a possessive (GR-8), which STE permits. Only the closed set of words below
# commonly contract "is"/"has" in technical prose; possessive nouns never match this list.
CONTRACTION = re.compile(
    r"\b[A-Za-z]+n't\b"
    r"|\b[A-Za-z]+['’](?:re|ve|ll|d|m)\b"
    r"|\b(?:it|that|this|there|here|what|who|one|let)['’]s\b",
    re.I,
)
AUXILIARY = re.compile(r"\b(?:has|have|had|is|are|was|were|be|being|been)\s+[A-Za-z-]+(?:ed|ing)\b", re.I)
# Rule 3.4 explicitly bans a modal ("must", "will", "can", ...) plus "be" plus a
# past-participle/-ing word — a distinct, higher-confidence pattern from the generic
# AUXILIARY heuristic above (which also catches allowed adjectival past participles).
MODAL_BE = re.compile(r"\b(?:can|could|shall|should|will|would|may|might|must)\s+be\s+[A-Za-z-]+(?:ed|ing)\b", re.I)
PASSIVE = re.compile(r"\b(?:is|are|was|were|be|been|being)\s+[A-Za-z-]+ed\b(?:\s+by\b)?", re.I)
NOTE = re.compile(r"^\s*(?:NOTE|Note):", re.I)
COMMAND = re.compile(r"\b(?:do not|don't|make sure|install|remove|set|check|verify|connect|disconnect|open|close|read|use|apply|measure|adjust|ensure)\b", re.I)
SAFETY = re.compile(r"^\s*(?:WARNING|CAUTION|DANGER|Warning|Caution|Danger):", re.I)
SEMICOLON = re.compile(r";")


def words(line: str) -> int:
    # Hyphenated compounds count as one token for this triage check.
    return len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", line))


def finding(code: str, severity: str, line_no: int, message: str, evidence: str) -> dict:
    return {"code": code, "severity": severity, "line": line_no, "message": message, "evidence": evidence.strip()}


def audit(text: str, procedural: bool) -> list[dict]:
    findings: list[dict] = []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        is_note = bool(NOTE.search(line))
        if CONTRACTION.search(line):
            findings.append(finding("STE-04.2", "MAJOR", number, "Contraction detected; write all words in full.", line))
        if SEMICOLON.search(line):
            findings.append(finding("STE-08.1", "MAJOR", number, "Semicolon detected; STE prohibits it, split into two sentences.", line))
        if is_note:
            if COMMAND.search(line):
                findings.append(finding("STE-05.5", "MAJOR", number, "Note appears to contain an instruction; classify and move it.", line))
            count = words(line)
            if count > 25:
                findings.append(finding("STE-05.5", "MAJOR", number, f"Note sentence has {count} words; maximum is 25.", line))
        elif procedural or SAFETY.search(line):
            count = words(line)
            if count > 20:
                findings.append(finding("STE-05.1", "MAJOR", number, f"Procedural/safety sentence has {count} words; maximum is 20.", line))
        if MODAL_BE.search(line):
            findings.append(finding("STE-03.4", "MAJOR", number, "Modal auxiliary plus 'be' plus participle detected; rule 3.4 bans this construction, restructure as imperative or active voice.", line))
        elif AUXILIARY.search(line):
            findings.append(finding("STE-03.4", "MINOR", number, "Possible complex auxiliary or progressive verb construction; verify against the dictionary.", line))
        if PASSIVE.search(line) and not SAFETY.search(line):
            findings.append(finding("STE-03.6", "MINOR", number, "Possible passive voice; justify an unknown agent or rewrite actively.", line))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--procedural", action="store_true", help="apply the 20-word limit to non-safety lines")
    parser.add_argument("--json", action="store_true", help="emit machine-readable findings")
    args = parser.parse_args()
    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {args.file}: {exc}", file=sys.stderr)
        return 2
    findings = audit(text, args.procedural)
    if args.json:
        print(json.dumps(findings, indent=2))
    elif findings:
        for item in findings:
            print(f"{item['severity']} {item['code']}:{item['line']}: {item['message']} :: {item['evidence']}")
        print(f"{len(findings)} candidate finding(s); triage each against audit/00-severity.md before it counts toward the gate.")
        print("Dictionary, terminology, and meaning checks require the human/agent audit files and an authoritative source.")
    else:
        print("No mechanical findings. This is not dictionary approval or STE certification, and does not by itself satisfy the audit gate.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
