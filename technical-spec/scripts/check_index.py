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


def find_problems(specs_dir):
    on_disk = {}
    for p in glob.glob(os.path.join(specs_dir, "*.md")):
        base = os.path.basename(p)
        m = FILE_RE.match(base)
        if m:
            on_disk[base] = int(m.group(1))
    with open(os.path.join(specs_dir, "_index.md"), encoding="utf-8") as f:
        linked = {l for l in LINK_RE.findall(f.read()) if FILE_RE.match(l)}
    problems = [f"linked in _index.md but missing on disk: {m}" for m in sorted(linked - set(on_disk))]
    problems += [f"on disk but not linked from _index.md: {u}" for u in sorted(set(on_disk) - linked)]
    nums = sorted(on_disk.values())
    for prev, cur in zip(nums, nums[1:]):
        problems += [f"numbering gap: no file numbered {gap:02d}" for gap in range(prev + 1, cur)]
    return problems, len(on_disk)


def self_test():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for name in ("01-overview.md", "03-stack.md"):
            open(os.path.join(d, name), "w").close()
        with open(os.path.join(d, "_index.md"), "w") as f:
            f.write("- [Overview](01-overview.md)\n- [Data](02-data.md)\n")
        problems, _ = find_problems(d)
        assert any("missing on disk: 02-data.md" in p for p in problems), problems
        assert any("not linked from _index.md: 03-stack.md" in p for p in problems), problems
        assert any("no file numbered 02" in p for p in problems), problems
    print("self-test OK")


def main():
    if sys.argv[1:] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--specs-dir", default="docs/technical-specs")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(args.specs_dir, "_index.md")):
        sys.exit(f"No _index.md in {args.specs_dir}")
    problems, count = find_problems(args.specs_dir)
    if problems:
        print("Technical-spec index problems:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: _index.md matches {count} spec files.")


if __name__ == "__main__":
    main()
