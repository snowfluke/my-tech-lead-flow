#!/usr/bin/env python3
"""Check that every AC ID referenced in a file actually exists in docs/business.

Catches fabricated or stale acceptance-criteria citations. The set of valid AC
IDs is collected from the `### AC-XX.YY` headings in
docs/business/acceptance-criteria-breakdown/*.md (falling back to
acceptance-criteria.md). Any AC-XX.YY referenced in the target files that is
not in that set is reported.

Usage:
  python check_ac_refs.py [target ...] [--business-dir docs/business]

Default target is docs/TASK_BREAKDOWN.md. Exit status is non-zero if any
referenced AC ID is missing, so it is usable as a CI gate.
"""
import argparse
import glob
import os
import re
import sys

AC_REF_RE = re.compile(r"\bAC-\d+\.\d+\b")
AC_DEF_RE = re.compile(r"^###\s+(AC-\d+\.\d+)\b", re.MULTILINE)
AC_INDEX_RE = re.compile(r"\bAC-\d+\.\d+\b")


def valid_ac_ids(business_dir):
    ids = set()
    breakdown = os.path.join(business_dir, "acceptance-criteria-breakdown")
    files = glob.glob(os.path.join(breakdown, "*.md"))
    for p in files:
        with open(p, encoding="utf-8") as f:
            ids.update(AC_DEF_RE.findall(f.read()))
    if not ids:
        idx = os.path.join(business_dir, "acceptance-criteria.md")
        if os.path.exists(idx):
            with open(idx, encoding="utf-8") as f:
                ids.update(AC_INDEX_RE.findall(f.read()))
    return ids


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="*", default=["docs/TASK_BREAKDOWN.md"])
    ap.add_argument("--business-dir", default="docs/business")
    args = ap.parse_args()

    valid = valid_ac_ids(args.business_dir)
    if not valid:
        sys.exit(f"No AC definitions found under {args.business_dir}; cannot validate.")

    missing = {}
    for t in args.targets:
        if not os.path.exists(t):
            print(f"warning: target not found: {t}", file=sys.stderr)
            continue
        with open(t, encoding="utf-8") as f:
            for ref in AC_REF_RE.findall(f.read()):
                if ref not in valid:
                    missing.setdefault(ref, []).append(t)

    if missing:
        print("Referenced AC IDs not found in docs/business:", file=sys.stderr)
        for ref in sorted(missing):
            print(f"  - {ref} (cited in {', '.join(sorted(set(missing[ref])))})",
                  file=sys.stderr)
        sys.exit(1)
    print(f"OK: all referenced AC IDs exist ({len(valid)} defined).")


if __name__ == "__main__":
    main()
