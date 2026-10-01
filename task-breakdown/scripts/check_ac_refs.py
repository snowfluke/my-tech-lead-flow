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
# A copy of this file lives in lead-review/scripts/. Each skill installs on its own; change both.
import argparse
import glob
import os
import re
import sys

AC_REF_RE = re.compile(r"\bAC-(\d+)\.(\d+)(?:-(\d+))?\b")  # AC-16.01, or a range AC-16.01-03
AC_DEF_RE = re.compile(r"^###\s+(AC-\d+\.\d+)\b", re.MULTILINE)
AC_INDEX_RE = re.compile(r"\bAC-\d+\.\d+\b")


def guard(path):
    """Unattended mode (a review bot holding credentials) reads only files whose real path lies under
    LEAD_REVIEW_ROOTS, a colon-separated list. Without it, it reads nothing: the guard fails closed.
    The real path counts, so `..` segments and symlinks that leave the roots are refused."""
    if os.environ.get("LEAD_REVIEW_UNATTENDED") != "1":
        return path
    roots = [os.path.realpath(r) for r in os.environ.get("LEAD_REVIEW_ROOTS", "").split(":") if r]
    real = os.path.realpath(path)
    if not any(real == r or real.startswith(r + os.sep) for r in roots):
        sys.exit(f"unattended mode: {path!r} is outside LEAD_REVIEW_ROOTS; refused")
    return path


def valid_ac_ids(business_dir):
    """AC IDs defined in the business docs. A file (an older project's single AC table) defines every ID it names."""
    if os.path.isfile(business_dir):
        with open(guard(business_dir), encoding="utf-8") as f:
            return set(AC_INDEX_RE.findall(f.read()))
    ids = set()
    breakdown = os.path.join(business_dir, "acceptance-criteria-breakdown")
    files = glob.glob(os.path.join(breakdown, "*.md"))
    for p in files:
        with open(guard(p), encoding="utf-8") as f:
            ids.update(AC_DEF_RE.findall(f.read()))
    if not ids:
        idx = os.path.join(business_dir, "acceptance-criteria.md")
        if os.path.exists(idx):
            with open(guard(idx), encoding="utf-8") as f:
                ids.update(AC_INDEX_RE.findall(f.read()))
    return ids


def cited_ids(text):
    """Every AC ID the text cites; a range AC-16.01-03 cites AC-16.01, AC-16.02, and AC-16.03."""
    ids = []
    for story, first, last in AC_REF_RE.findall(text):
        width = len(first)
        for seq in range(int(first), int(last or first) + 1):
            ids.append(f"AC-{story}.{seq:0{width}d}")
    return ids


def find_missing(targets, valid):
    missing = {}
    for t in targets:
        if not os.path.exists(t):
            missing.setdefault("(target not found)", []).append(t)
            continue
        with open(guard(t), encoding="utf-8") as f:
            for ref in cited_ids(f.read()):
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
        assert cited_ids("AC-16.01-03 and AC-02.05") == ["AC-16.01", "AC-16.02", "AC-16.03", "AC-02.05"]
        with open(target, "w") as f:
            f.write("Covers AC-01.01-03.\n")
        assert list(find_missing([target], valid)) == ["AC-01.03"], "the end of a range must be checked"
    # The unattended-mode guard: fails closed, and refuses .. and symlinks that leave the roots.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        inside = os.path.join(d, "in")
        os.makedirs(inside)
        ok_file = os.path.join(inside, "a.md")
        with open(ok_file, "w") as fh:
            fh.write("x")
        os.symlink(os.path.realpath(__file__), os.path.join(inside, "link.md"))
        saved = {k: os.environ.get(k) for k in ("LEAD_REVIEW_UNATTENDED", "LEAD_REVIEW_ROOTS")}

        def refused(path):
            try:
                guard(path)
            except SystemExit:
                return True
            return False
        try:
            os.environ["LEAD_REVIEW_UNATTENDED"] = "1"
            os.environ.pop("LEAD_REVIEW_ROOTS", None)
            assert refused(ok_file), "unattended mode with no roots must refuse every file"
            os.environ["LEAD_REVIEW_ROOTS"] = inside
            assert not refused(ok_file), "a file under the roots must pass"
            assert refused(os.path.join(inside, "..", "..", "..", "etc", "hosts")), "a .. escape must be refused"
            assert refused(os.path.join(inside, "link.md")), "a symlink out of the roots must be refused"
        finally:
            for k, v in saved.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
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
            targets += sorted(os.path.join(t, f) for f in os.listdir(guard(t)) if f.endswith(".md"))
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
