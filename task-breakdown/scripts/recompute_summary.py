#!/usr/bin/env python3
"""Recompute the task breakdown's Summary table and validate Card IDs.

The Summary table (BE/FE card counts and Est sums per sprint) is derived from
the per-sprint card tables. LLMs make silent counting and arithmetic errors
here, so this recomputes it deterministically. It also flags duplicate Card
IDs and non-sequential numbering within a role+sprint.

The task breakdown is a folder (docs/task-breakdown/ with _index.md,
team-and-process.md, and one sprint-N.md per sprint) or, in an older project,
one TASK_BREAKDOWN.md file. For a folder the Summary table lives in _index.md
and links each sprint to its file.

Usage:
  python3 recompute_summary.py [docs/task-breakdown | path/to/TASK_BREAKDOWN.md] [--write]
  python3 recompute_summary.py --self-test

Without --write it prints the regenerated Summary table and any warnings.
With --write it replaces the existing `## Summary` section in place.
Exit status is non-zero for a malformed or duplicate Card ID. A numbering gap only
prints a warning, because renumbering breaks issues that already name the card.
"""
import argparse
import os
import re
import sys

SPRINT_RE = re.compile(r"^#{1,2}\s+Sprint\s+(\d+)\s*[:—-]\s*(.+?)\s*$")
SUBSECTION_RE = re.compile(r"^###\s+(Backend|Frontend)\b", re.IGNORECASE)
OTHER_H2_RE = re.compile(r"^##\s+(?!Sprint\b)")
CARD_ID_RE = re.compile(r"^(BE|FE|TL|DB)-S(\d+)-(\d+)$")
EST_RE = re.compile(r"([0-9]*\.?[0-9]+)\s*d", re.IGNORECASE)


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(line):
    return bool(re.match(r"^\s*\|[\s:|-]+\|\s*$", line))


def sources(path):
    """[(file name, lines)] for a folder's sprint files, or the one file."""
    if os.path.isdir(path):
        names = sorted((f for f in os.listdir(path) if re.match(r"sprint-\d+\.md$", f)),
                       key=lambda f: int(re.findall(r"\d+", f)[0]))
        out = []
        for name in names:
            with open(os.path.join(path, name), encoding="utf-8") as f:
                out.append((name, f.readlines()))
        return out
    with open(path, encoding="utf-8") as f:
        return [(os.path.basename(path), f.readlines())]


def parse(path):
    sprints, tally, card_ids, files = parse_sources(sources(path))
    return sprints, tally, card_ids, files


def parse_sources(srcs):
    sprints = []          # [(num, focus)]
    tally = {}            # (sprint, role) -> {"cards": int, "est": float}
    card_ids = []         # [(card_id, role, sprint, seq, "file:line")]
    files = {}            # sprint -> file name
    for fname, lines in srcs:
        cur_sprint = None
        cur_role = None
        header_cols = None
        for i, line in enumerate(lines):
            ms = SPRINT_RE.match(line)
            if ms:
                cur_sprint = int(ms.group(1))
                if cur_sprint not in [n for n, _ in sprints]:
                    sprints.append((cur_sprint, ms.group(2).strip()))
                    files[cur_sprint] = fname
                cur_role = None
                header_cols = None
                continue
            if OTHER_H2_RE.match(line):  # left the sprint area (e.g. ## Summary, ## DoD)
                cur_sprint = None
                cur_role = None
                continue
            msub = SUBSECTION_RE.match(line)
            if msub and cur_sprint is not None:
                cur_role = "BE" if msub.group(1).lower() == "backend" else "FE"
                header_cols = None
                tally.setdefault((cur_sprint, cur_role), {"cards": 0, "est": 0.0})
                continue
            if cur_sprint is not None and cur_role and line.lstrip().startswith("|"):
                if is_separator(line):
                    continue
                cells = split_row(line)
                if header_cols is None:
                    header_cols = [c.lower() for c in cells]
                    continue
                row = dict(zip(header_cols, cells))
                cid = row.get("card id", cells[0] if cells else "").strip().strip("`")
                m = CARD_ID_RE.match(cid)
                if m:
                    card_ids.append((cid, m.group(1), int(m.group(2)), int(m.group(3)), f"{fname}:{i + 1}"))
                else:
                    card_ids.append((cid, None, cur_sprint, None, f"{fname}:{i + 1}"))
                tally[(cur_sprint, cur_role)]["cards"] += 1
                mest = EST_RE.search(row.get("est", ""))
                if mest:
                    tally[(cur_sprint, cur_role)]["est"] += float(mest.group(1))
    return sprints, tally, card_ids, files


def fmt_est(v):
    if v == 0:
        return "-"
    return f"{round(v, 1):g}d"


def build_summary(sprints, tally, files=None):
    rows = ["## Summary", "",
            "| Sprint | Focus | BE cards | FE cards | BE Est | FE Est |",
            "| ------ | ----- | -------- | -------- | ------ | ------ |"]
    for num, focus in sprints:
        be = tally.get((num, "BE"))
        fe = tally.get((num, "FE"))
        be_cards = str(be["cards"]) if be and be["cards"] else "-"
        fe_cards = str(fe["cards"]) if fe and fe["cards"] else "-"
        be_est = fmt_est(be["est"]) if be else "-"
        fe_est = fmt_est(fe["est"]) if fe else "-"
        label = f"[S{num}]({files[num]})" if files else f"S{num}"
        rows.append(f"| {label} | {focus} | {be_cards} | {fe_cards} | {be_est} | {fe_est} |")
    return "\n".join(rows)


def validate_ids(card_ids):
    """Return (errors, warnings). A malformed or duplicate ID is an error; a numbering gap is only a warning,
    because renumbering a card breaks the issue that already names it."""
    errors, warnings, seen = [], [], {}
    for cid, role, sprint, seq, where in card_ids:
        if role is None:
            errors.append(f"{where}: {cid!r} is not a Card ID; use <BE|FE|TL|DB>-S<sprint>-<NN>")
        elif cid in seen:
            errors.append(f"Duplicate Card ID {cid} ({seen[cid]} and {where})")
        else:
            seen[cid] = where
    groups = {}
    for cid, role, sprint, seq, where in card_ids:
        if role is not None:
            groups.setdefault((role, sprint), []).append(seq)
    for (role, sprint), seqs in sorted(groups.items()):
        s = sorted(seqs)
        if s != list(range(1, len(s) + 1)):
            warnings.append(f"{role}-S{sprint} numbering has gaps: {s}. Keep the IDs; do not renumber.")
    return errors, warnings


def replace_summary(lines, new_summary):
    text = "".join(lines)
    m = re.search(r"(?m)^## Summary[ \t]*$", text)  # exact heading; "## Summary by Sprint" is not ours
    if m is None:
        return text.rstrip() + "\n\n" + new_summary + "\n"
    idx = m.start() - 1
    head = text[: idx + 1]
    rest = text[idx + 1 :]
    # find next H2 after the Summary heading
    nxt = re.search(r"\n##\s+(?!Summary)", rest)
    tail = rest[nxt.start():] if nxt else ""
    return head + new_summary + ("\n" + tail.lstrip("\n") if tail else "\n")


def self_test():
    sprint = ["# Sprint 1: Auth\n", "\n", "### Backend\n", "\n",
              "| Card ID | PM Card Title | Task Description | AC | Owner | Est | Docs |\n",
              "| --- | --- | --- | --- | --- | --- | --- |\n",
              "| BE-S1-01 | Login | x | AC-01.01 | BE1 | 2d | - |\n",
              "| BE-S1-02 | Logout | x | AC-01.02 | BE1 | 1.5d | - |\n",
              "\n", "### Frontend\n", "\n",
              "| Card ID | PM Card Title | Task Description | AC | Owner | Est | Docs |\n",
              "| --- | --- | --- | --- | --- | --- | --- |\n",
              "| FE-S1-01 | Login page | x | AC-01.01 | FE1 | 1d | - |\n"]
    sprints, tally, ids, files = parse_sources([("sprint-1.md", sprint)])
    assert tally[(1, "BE")] == {"cards": 2, "est": 3.5} and tally[(1, "FE")]["cards"] == 1, tally
    table = build_summary(sprints, tally, files)
    assert "| [S1](sprint-1.md) | Auth | 2 | 1 | 3.5d | 1d |" in table, table
    assert validate_ids(ids) == ([], [])
    dup = sprint[:7] + ["| BE-S1-01 | Again | x | AC-01.03 | BE1 | 1d | - |\n"] + sprint[8:]
    assert validate_ids(parse_sources([("sprint-1.md", dup)])[2])[0], "duplicate Card ID not caught"
    wire = sprint[:7] + ["| BE-S1-WIRE | Wire login | x | AC-01.01 | BE1 | 1d | - |\n"] * 2 + sprint[8:]
    assert validate_ids(parse_sources([("sprint-1.md", wire)])[2])[0], "a -WIRE ID must be rejected"
    gap = sprint[:7] + ["| BE-S1-03 | Later | x | AC-01.03 | BE1 | 1d | - |\n"] + sprint[8:]
    errors, warnings = validate_ids(parse_sources([("sprint-1.md", gap)])[2])
    assert not errors and warnings, (errors, warnings)
    single = ["## Sprint 1: Auth\n"] + sprint[1:] + ["\n", "## Summary\n"]
    assert parse_sources([("TASK_BREAKDOWN.md", single)])[1][(1, "BE")]["cards"] == 2
    legacy = ["## Module: Tasks\n", "### Priority: HIGH\n", "| ID | Title | Role |\n", "| --- | --- | --- |\n",
              "| TASK-01 | Board | BE |\n", "\n", "## Summary by Sprint\n", "| S1 | 20 |\n"]
    assert parse_sources([("TASK_BREAKDOWN.md", legacy)])[0] == [], "a foreign layout must yield no sprints"
    kept = replace_summary(legacy, "## Summary\n\nnew")
    assert "## Summary by Sprint\n| S1 | 20 |" in kept, "a similar heading must never be replaced"
    print("self-test OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", default="docs/task-breakdown")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    sprints, tally, card_ids, files = parse(args.path)
    if not sprints:
        sys.exit(f"{args.path}: no '## Sprint N: <name>' sections found. This board uses its own layout. "
                 "Update its summary by hand; this script reads only the task-breakdown layout and writes nothing.")
    folder = os.path.isdir(args.path)
    summary = build_summary(sprints, tally, files if folder else None)
    errors, warnings = validate_ids(card_ids)

    if args.write:
        target = os.path.join(args.path, "_index.md") if folder else args.path
        with open(target, encoding="utf-8") as f:
            lines = f.readlines()
        new_text = replace_summary(lines, summary)
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Updated Summary in {target}")
    else:
        print(summary)

    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if errors:
        print("\nCard ID errors:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
