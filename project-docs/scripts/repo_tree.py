#!/usr/bin/env python3
"""Print an annotated repository tree for README / onboarding docs.

Produces a clean directory tree skipping the usual noise (VCS, dependencies,
build output, caches). The model adds per-folder purpose annotations after the
`#` markers; this script just produces the accurate structure so the model
does not transcribe a tree by hand and get it wrong.

Usage:
  python repo_tree.py [root] [--max-depth N] [--include-files]

By default it shows directories plus a representative sample of files per
directory. Use --include-files to list every file.
"""
import argparse
import os

DEFAULT_IGNORES = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", ".next", "out",
    "target", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache",
    ".turbo", ".cache", "coverage", ".idea", ".vscode", ".DS_Store", "vendor",
}


def tree(root, max_depth, include_files, ignores):
    lines = [os.path.basename(os.path.abspath(root)) + "/"]

    def walk(path, prefix, depth):
        if depth > max_depth:
            return
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name))
        except PermissionError:
            return
        entries = [e for e in entries if e.name not in ignores
                   and not e.name.startswith(".") or e.name in (".github", ".env.example")]
        dirs = [e for e in entries if e.is_dir()]
        files = [e for e in entries if e.is_file()]
        if not include_files and len(files) > 6:
            files = files[:6]
            truncated = True
        else:
            truncated = False
        shown = dirs + files
        for i, e in enumerate(shown):
            last = i == len(shown) - 1 and not truncated
            connector = "└── " if last else "├── "
            lines.append(prefix + connector + e.name + ("/" if e.is_dir() else ""))
            if e.is_dir():
                ext = "    " if last else "│   "
                walk(e.path, prefix + ext, depth + 1)
        if truncated:
            lines.append(prefix + "└── ...")

    walk(root, "", 1)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--max-depth", type=int, default=3)
    ap.add_argument("--include-files", action="store_true")
    args = ap.parse_args()
    print("```")
    print(tree(args.root, args.max_depth, args.include_files, DEFAULT_IGNORES))
    print("```")


if __name__ == "__main__":
    main()
