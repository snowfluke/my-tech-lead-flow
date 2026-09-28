#!/usr/bin/env python3
"""Check a triage log: one row per input item, each with a class and a target.

  check_triage.py LOG --items N [--ac-id REGEX]
  check_triage.py --self-test

See ../references/log-format.md for the table. Standard library only.
"""
import re
import sys

HEAD = "| Item | Summary | Class | AC | Target | Why |"
CLASSES = ("Bug", "Change", "Duplicate", "Later", "Not a defect")
AC_ID = r"AC-\d+(?:\.\d+)*"
MAX_SUMMARY_WORDS = 12


def rows(text):
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == HEAD)
    except StopIteration:
        return None
    out = []
    for n, line in enumerate(lines[start + 2:], start + 3):
        if not line.startswith("|"):
            break
        out.append((n, [c.strip() for c in line.strip().strip("|").split("|")]))
    return out


def check(text, items, ac_id=AC_ID):
    errs = [f"line {n}: non-ASCII {c!r}; ASCII only"
            for n, line in enumerate(text.splitlines(), 1) for c in sorted({c for c in line if ord(c) > 127})]
    table = rows(text)
    if table is None:
        return errs + [f"no table with the header: {HEAD}"]
    seen = set()
    for n, cells in table:
        if len(cells) != 6:
            errs.append(f"line {n}: {len(cells)} cells, need 6")
            continue
        item, summary, cls, ac, target, why = cells
        if item in seen:
            errs.append(f"line {n}: item {item} appears twice")
        seen.add(item)
        if cls not in CLASSES:
            errs.append(f"line {n}: class {cls!r} is not one of: {', '.join(CLASSES)}")
        if len(summary.split()) > MAX_SUMMARY_WORDS:
            errs.append(f"line {n}: summary over {MAX_SUMMARY_WORDS} words")
        if ac != "-" and not re.fullmatch(ac_id, ac):
            errs.append(f"line {n}: AC {ac!r} is not an AC ID or '-'")
        if cls == "Bug" and ac == "-":
            errs.append(f"line {n}: a Bug cites the AC it breaks. With no AC, it is a Change.")
        if cls == "Not a defect":
            if target != "-":
                errs.append(f"line {n}: a Not a defect row has no issue; its Target is '-'")
        elif not re.fullmatch(r"#\d+", target):
            errs.append(f"line {n}: a {cls} row needs an issue number as its Target, got {target!r}")
        if why in ("", "-"):
            errs.append(f"line {n}: Why is empty")
    if len(table) != items:
        errs.append(f"the log has {len(table)} rows, the round has {items} items")
    return errs


GOOD = """# SIT round 1 triage

Source: sit-1.csv, 2026-10-02. Items: 3.

| Item | Summary | Class | AC | Target | Why |
| --- | --- | --- | --- | --- | --- |
| SIT-01 | Export ignores the status filter | Bug | AC-29.02 | #57 | The THEN clause says visible rows only. |
| SIT-02 | Export should include comments | Change | - | #58 | No AC covers comments. |
| SIT-03 | Date shows in UTC | Not a defect | AC-29.05 | - | AC-29.05 says UTC. |
"""


def self_test():
    assert check(GOOD, 3) == [], check(GOOD, 3)
    bad = {
        "lost item": (GOOD, 4),
        "Bug without AC": (GOOD.replace("| Bug | AC-29.02 |", "| Bug | - |"), 3),
        "Bug without issue": (GOOD.replace("| #57 |", "| - |"), 3),
        "Not a defect with issue": (GOOD.replace("| AC-29.05 | - |", "| AC-29.05 | #9 |"), 3),
        "unknown class": (GOOD.replace("| Change |", "| Feature |"), 3),
        "empty why": (GOOD.replace("No AC covers comments.", "-"), 3),
        "duplicate item": (GOOD.replace("SIT-02", "SIT-01"), 3),
        "bad AC": (GOOD.replace("AC-29.02", "29.02"), 3),
        "non-ASCII": (GOOD.replace("visible rows only.", "visible rows — only."), 3),
        "no table": ("# Triage\n", 0),
        "short row": (GOOD.replace("| #58 | No AC covers comments. |", "| #58 |"), 3),
    }
    for name, (text, items) in bad.items():
        assert check(text, items), f"self-test: '{name}' was not caught"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="check_triage.py")
    ap.add_argument("log")
    ap.add_argument("--items", type=int, required=True, help="the number of items in the round's results")
    ap.add_argument("--ac-id", default=AC_ID, help="the project's AC ID pattern")
    a = ap.parse_args(argv)
    with open(a.log, encoding="utf-8") as f:
        errs = check(f.read(), a.items, a.ac_id)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    print("triage log OK")


if __name__ == "__main__":
    main(sys.argv[1:])
