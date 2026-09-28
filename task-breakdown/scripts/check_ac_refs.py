#!/usr/bin/env python3
"""Check that every AC ID referenced in a file actually exists in docs/business.

Catches fabricated or stale acceptance-criteria citations. The set of valid AC
IDs is collected from the `### AC-XX.YY` headings in
docs/business/acceptance-criteria-breakdown/*.md (falling back to
acceptance-criteria.md). Any AC-XX.YY referenced in the target files that is
not in that set is reported.

Usage:
  python3 check_ac_refs.py [target ...] [--business-dir docs/business]
  python3 check_ac_refs.py --self-test

A target may be a folder; every .md file in it is checked. Default target is
docs/task-breakdown/ (the folder form of the task breakdown). Exit status is non-zero if any
referenced AC ID is missing, so it is usable as a CI gate.
"""
# A copy of this file lives in code-review/scripts/. Each skill installs on its own; change both.
import argparse
import glob
import os
import re
import sys

AC_REF_RE = re.compile(r"\bAC-\d+\.\d+\b")
AC_DEF_RE = re.compile(r"^###\s+(AC-\d+\.\d+)\b", re.MULTILINE)
AC_INDEX_RE = re.compile(r"\bAC-\d+\.\d+\b")


def valid_ac_ids(business_dir):
    """AC IDs defined in the business docs. A file (an older project's single AC table) defines every ID it names."""
    if os.path.isfile(business_dir):
        with open(business_dir, encoding="utf-8") as f:
            return set(AC_INDEX_RE.findall(f.read()))
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


def find_missing(targets, valid):
    missing = {}
    for t in targets:
        if not os.path.exists(t):
            missing.setdefault("(target not found)", []).append(t)
            continue
        with open(t, encoding="utf-8") as f:
            for ref in AC_REF_RE.findall(f.read()):
                if ref not in valid:
                    missing.setdefault(ref, []).append(t)
    return missing


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "business", "acceptance-criteria-breakdown"))
        with open(os.path.join(root, "business", "acceptance-criteria-breakdown", "s1.md"), "w") as f:
            f.write("### AC-01.01 Login\n### AC-01.02 Logout\n")
        target = os.path.join(root, "card.md")
        with open(target, "w") as f:
            f.write("Covers AC-01.01 and AC-09.09.\n")
        valid = valid_ac_ids(os.path.join(root, "business"))
        assert valid == {"AC-01.01", "AC-01.02"}, valid
        assert list(find_missing([target], valid)) == ["AC-09.09"]
        assert find_missing([os.path.join(root, "nope.md")], valid), "a missing target must fail, not pass"
        legacy = os.path.join(root, "ACCEPTANCE_CRITERIA.md")
        with open(legacy, "w") as f:
            f.write("| AC-01.01 | x |\n| AC-09.09 | y |\n")
        assert find_missing([target], valid_ac_ids(legacy)) == {}, "a single AC table defines its IDs"
    print("self-test OK")


def main():
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="*", default=["docs/task-breakdown"])
    ap.add_argument("--business-dir", default="docs/business")
    args = ap.parse_args()

    valid = valid_ac_ids(args.business_dir)
    if not valid:
        sys.exit(f"No AC definitions found under {args.business_dir}; cannot validate.")

    targets = []
    for t in args.targets:
        if os.path.isdir(t):
            targets += sorted(os.path.join(t, f) for f in os.listdir(t) if f.endswith(".md"))
        else:
            targets.append(t)

    missing = find_missing(targets, valid)

    if missing:
        print("Missing targets or AC IDs not defined in the business docs:", file=sys.stderr)
        for ref in sorted(missing):
            print(f"  - {ref} (cited in {', '.join(sorted(set(missing[ref])))})",
                  file=sys.stderr)
        sys.exit(1)
    print(f"OK: all referenced AC IDs exist ({len(valid)} defined).")


if __name__ == "__main__":
    main()
