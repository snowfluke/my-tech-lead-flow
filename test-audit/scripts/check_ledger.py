#!/usr/bin/env python3
"""Check a test-audit ledger: every test has a mark and the evidence its mark needs.

  check_ledger.py LEDGER [--root PATH]
  check_ledger.py --self-test

--root is the repo root that the backticked paths are relative to (default:
the current directory). See ../references/ledger-format.md. Standard library only.
"""
import os
import re
import sys

HEAD = "| Test | Mark | Catches | History | Keeper | Unlocks | Check |"
MARKS = ("R", "F", "C", "D")
PATH_RE = re.compile(r"`([^`\s]+)`")
IN_SCOPE_RE = re.compile(r"Tests in scope: (\d+)\.")


def rows(text):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip() == HEAD), None)
    if start is None:
        return None
    out = []
    for n, line in enumerate(lines[start + 2:], start + 3):
        if not line.startswith("|"):
            break
        out.append((n, [c.strip() for c in line.strip().strip("|").split("|")]))
    return out


def check_path(cell, label, n, root, errs):
    m = PATH_RE.search(cell)
    if not m:
        errs.append(f"line {n}: {label} names no file in backticks")
    elif not os.path.exists(os.path.join(root, m.group(1))):
        errs.append(f"line {n}: {label} file `{m.group(1)}` does not exist")


def check(text, root="."):
    errs = [f"line {n}: non-ASCII {c!r}; ASCII only"
            for n, line in enumerate(text.splitlines(), 1) for c in sorted({c for c in line if ord(c) > 127})]
    table = rows(text)
    if table is None:
        return errs + [f"no table with the header: {HEAD}"]
    seen = set()
    for n, cells in table:
        if len(cells) != 7:
            errs.append(f"line {n}: {len(cells)} cells, need 7")
            continue
        test, mark, catches, history, keeper, unlocks, cmd = cells
        if test in seen:
            errs.append(f"line {n}: the test appears twice")
        seen.add(test)
        check_path(test, "Test", n, root, errs)
        if mark not in MARKS:
            errs.append(f"line {n}: mark {mark!r} is not one of: {', '.join(MARKS)}")
            continue
        if catches in ("", "-"):
            errs.append(f"line {n}: Catches is empty; say what regression it detects, or 'Nothing: <why>'")
        if mark in ("C", "D"):
            if history in ("", "-"):
                errs.append(f"line {n}: a {mark} row gives the History of the test")
            no_keeper = mark == "D" and keeper.startswith("None needed: ") and len(keeper.split()) > 3
            if not no_keeper:
                check_path(keeper, f"{mark} row Keeper", n, root, errs)
        elif keeper != "-":
            errs.append(f"line {n}: an {mark} row has no Keeper; use '-'")
        if mark in ("F", "C", "D") and cmd in ("", "-"):
            errs.append(f"line {n}: a {mark} row names the Check command that runs the keeper")
    m = IN_SCOPE_RE.search(text)
    if m and int(m.group(1)) != len(table):
        errs.append(f"the ledger has {len(table)} rows, but says {m.group(1)} tests are in scope")
    return errs


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "src/tasks"))
        for f in ("csv.test.ts", "export.routes.test.ts", "guard.test.ts"):
            open(os.path.join(root, "src/tasks", f), "w").close()
        good = (
            "# Test audit: tasks\n\nBase: abc. Tests in scope: 4.\n\n" + HEAD + "\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| `src/tasks/csv.test.ts` exports visible rows | R | A leak of hidden rows. | AC-29.02. | - | - | - |\n"
            "| `src/tasks/csv.test.ts` builds header | D | Nothing: the header comes from the code under test. | First CSV commit. | `src/tasks/export.routes.test.ts` returns the header | `buildHeaderForTest` | `bun test src/tasks` |\n"
            "| `src/tasks/guard.test.ts` rejects other project | F | Nothing today: the auth guard refuses first. | Scope fix. | - | - | `bun test src/tasks/guard.test.ts` |\n"
            "| `src/tasks/guard.test.ts` logs the call | D | Nothing: it asserts a log call no one reads. | Debug session. | None needed: no contract depends on the log line. | - | `bun test src/tasks` |\n"
        )
        assert check(good, root) == [], check(good, root)
        bad = {
            "unknown mark": good.replace("| R |", "| K |"),
            "D without keeper": good.replace("`src/tasks/export.routes.test.ts` returns the header", "-"),
            "made-up keeper": good.replace("export.routes.test.ts", "export.test.ts"),
            "made-up test file": good.replace("`src/tasks/csv.test.ts` exports", "`src/tasks/rows.test.ts` exports"),
            "D without history": good.replace("First CSV commit.", "-"),
            "F without check": good.replace("`bun test src/tasks/guard.test.ts`", "-"),
            "R with keeper": good.replace("| AC-29.02. | - |", "| AC-29.02. | `src/tasks/guard.test.ts` x |"),
            "empty catches": good.replace("A leak of hidden rows.", "-"),
            "bare None needed": good.replace("None needed: no contract depends on the log line.", "None needed: -"),
            "row count": good.replace("Tests in scope: 4.", "Tests in scope: 5."),
            "duplicate test": good.replace("builds header | D", "exports visible rows | D"),
            "non-ASCII": good.replace("A leak of hidden rows.", "A leak \u2192 hidden rows."),
            "no table": "# Test audit\n",
        }
        for name, text in bad.items():
            assert check(text, root), f"self-test: '{name}' was not caught"
    print("self-test OK")


def main(argv):
    if argv[:1] == ["--self-test"]:
        return self_test()
    import argparse
    ap = argparse.ArgumentParser(prog="check_ledger.py")
    ap.add_argument("ledger")
    ap.add_argument("--root", default=".", help="the repo root that paths are relative to")
    a = ap.parse_args(argv)
    with open(a.ledger, encoding="utf-8") as f:
        errs = check(f.read(), a.root)
    if errs:
        print("\n".join(f"- {e}" for e in errs), file=sys.stderr)
        sys.exit(1)
    print("ledger OK")


if __name__ == "__main__":
    main(sys.argv[1:])
