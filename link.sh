#!/bin/sh
# Link every skill in this repo into a skills directory (default: ~/.claude/skills).
# Edits made through the link land in this clone, ready to commit and push.
set -eu
repo=$(cd "$(dirname "$0")" && pwd)
target=${1:-"$HOME/.claude/skills"}
mkdir -p "$target"
for skill in "$repo"/*/SKILL.md; do
  dir=$(dirname "$skill")
  name=$(basename "$dir")
  if [ -e "$target/$name" ] && [ ! -L "$target/$name" ]; then
    echo "skip $name: $target/$name is a real directory" >&2
    continue
  fi
  ln -sfn "$dir" "$target/$name"
  echo "linked $name"
done
