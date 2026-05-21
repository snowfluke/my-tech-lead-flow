#!/usr/bin/env python3
"""Recompute the Summary table in TASK_BREAKDOWN.md and validate Card IDs.

The Summary table (BE/FE card counts and Est sums per sprint) is derived from
the per-sprint card tables. LLMs make silent counting and arithmetic errors
here, so this recomputes it deterministically. It also flags duplicate Card
IDs and non-sequential numbering within a role+sprint.

Usage:
  python recompute_summary.py [path/to/TASK_BREAKDOWN.md] [--write]

Without --write it prints the regenerated Summary table and any warnings.
With --write it replaces the existing `## Summary` section in place.
Exit status is non-zero if Card ID problems are found.
"""
import argparse
import re
import sys

SPRINT_RE = re.compile(r"^##\s+Sprint\s+(\d+)\s*[:—-]\s*(.+?)\s*$")
SUBSECTION_RE = re.compile(r"^###\s+(Backend|Frontend)\b", re.IGNORECASE)
OTHER_H2_RE = re.compile(r"^##\s+(?!Sprint\b)")
CARD_ID_RE = re.compile(r"^(BE|FE|TL|DB)-S(\d+)-(\d+)$")
EST_RE = re.compile(r"([0-9]*\.?[0-9]+)\s*d", re.IGNORECASE)


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def is_separator(line):
    return bool(re.match(r"^\s*\|[\s:|-]+\|\s*$", line))


def parse(path):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    sprints = []          # [(num, focus)]
    sprint_focus = {}
    # per (sprint, role) -> {"cards": int, "est": float}
    tally = {}
    card_ids = []         # [(card_id, role, sprint, seq, lineno)]

    cur_sprint = None
    cur_role = None
    header_cols = None

    for i, line in enumerate(lines):
        ms = SPRINT_RE.match(line)
        if ms:
            cur_sprint = int(ms.group(1))
            sprint_focus[cur_sprint] = ms.group(2).strip()
            if cur_sprint not in [s for s, _ in sprints]:
                sprints.append((cur_sprint, ms.group(2).strip()))
            cur_role = None
            header_cols = None
            continue
        if OTHER_H2_RE.match(line):  # left the sprint area (e.g. ## Summary, ## DoD)
            cur_sprint = None
            cur_role = None
            continue
        msub = SUBSECTION_RE.match(line)
        if msub and cur_sprint is not None:
            cur_role = msub.group(1).upper()[:2]  # BACKEND->BA? fix below
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
                continue  # header row
            # data row
            row = dict(zip(header_cols, cells))
            cid = row.get("card id", cells[0] if cells else "").strip().strip("`")
            m = CARD_ID_RE.match(cid)
            if m:
                card_ids.append((cid, m.group(1), int(m.group(2)), int(m.group(3)), i + 1))
            tally[(cur_sprint, cur_role)]["cards"] += 1
            est_cell = row.get("est", "")
            mest = EST_RE.search(est_cell)
            if mest:
                tally[(cur_sprint, cur_role)]["est"] += float(mest.group(1))

    return lines, sprints, tally, card_ids


def fmt_est(v):
    if v == 0:
        return "-"
    return f"{round(v, 1):g}d"


def build_summary(sprints, tally):
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
        rows.append(f"| S{num} | {focus} | {be_cards} | {fe_cards} | {be_est} | {fe_est} |")
    return "\n".join(rows)


def validate_ids(card_ids):
    warnings = []
    seen = {}
    for cid, role, sprint, seq, lineno in card_ids:
        if cid in seen:
            warnings.append(f"Duplicate Card ID {cid} (lines {seen[cid]} and {lineno})")
        else:
            seen[cid] = lineno
    # sequential check per (role, sprint)
    groups = {}
    for cid, role, sprint, seq, lineno in card_ids:
        groups.setdefault((role, sprint), []).append(seq)
    for (role, sprint), seqs in sorted(groups.items()):
        s = sorted(seqs)
        expected = list(range(1, len(s) + 1))
        if s != expected:
            warnings.append(
                f"{role}-S{sprint} numbering not 1..N sequential: found {s}"
            )
    return warnings


def replace_summary(lines, new_summary):
    text = "".join(lines)
    idx = text.find("\n## Summary")
    if idx == -1:
        # append
        return text.rstrip() + "\n\n" + new_summary + "\n"
    head = text[: idx + 1]
    rest = text[idx + 1 :]
    # find next H2 after the Summary heading
    nxt = re.search(r"\n##\s+(?!Summary)", rest)
    tail = rest[nxt.start():] if nxt else ""
    return head + new_summary + ("\n" + tail.lstrip("\n") if tail else "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", nargs="?", default="docs/TASK_BREAKDOWN.md")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lines, sprints, tally, card_ids = parse(args.path)
    summary = build_summary(sprints, tally)
    warnings = validate_ids(card_ids)

    if args.write:
        new_text = replace_summary(lines, summary)
        with open(args.path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"Updated Summary in {args.path}")
    else:
        print(summary)

    if warnings:
        print("\nCard ID warnings:", file=sys.stderr)
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
