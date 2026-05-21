#!/usr/bin/env python3
"""Verify _index.md stays in sync with the NN-*.md files on disk.

The technical-specs set is a numbered file set whose _index.md table of
contents must match the files present. This reports entries linked in the
index that are missing on disk, files on disk not linked from the index, and
gaps in the NN numbering.

Usage:
  python check_index.py [--specs-dir docs/technical-specs]

Exit status is non-zero on any mismatch, so it is usable as a CI gate.
"""
import argparse
import glob
import os
import re
import sys

FILE_RE = re.compile(r"^(\d+)-[\w-]+\.md$")
LINK_RE = re.compile(r"\((\d+-[\w-]+\.md)\)")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--specs-dir", default="docs/technical-specs")
    args = ap.parse_args()

    index_path = os.path.join(args.specs_dir, "_index.md")
    if not os.path.exists(index_path):
        sys.exit(f"No _index.md in {args.specs_dir}")

    on_disk = {}
    for p in glob.glob(os.path.join(args.specs_dir, "*.md")):
        base = os.path.basename(p)
        m = FILE_RE.match(base)
        if m:
            on_disk[base] = int(m.group(1))

    with open(index_path, encoding="utf-8") as f:
        linked = set(LINK_RE.findall(f.read()))
    linked = {l for l in linked if FILE_RE.match(l)}

    disk_set = set(on_disk)
    problems = []

    for missing in sorted(linked - disk_set):
        problems.append(f"linked in _index.md but missing on disk: {missing}")
    for unlinked in sorted(disk_set - linked):
        problems.append(f"on disk but not linked from _index.md: {unlinked}")

    nums = sorted(on_disk.values())
    for prev, cur in zip(nums, nums[1:]):
        for gap in range(prev + 1, cur):
            problems.append(f"numbering gap: no file numbered {gap:02d}")

    if problems:
        print("Technical-spec index problems:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: _index.md matches {len(disk_set)} spec files.")


if __name__ == "__main__":
    main()
