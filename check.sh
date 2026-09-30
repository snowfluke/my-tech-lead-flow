#!/bin/sh
# Run before every push; CI runs it too. Every skill must install with the
# skills CLI, whose YAML parser is stricter than Claude Code's, and every
# script must pass its self-test.
set -u
cd "$(dirname "$0")"
fail=0
for f in */scripts/*.py; do
  python3 "$f" --self-test >/dev/null 2>&1 || { echo "FAIL self-test: $f"; fail=1; }
done
want=$(ls -d */SKILL.md | wc -l | tr -d ' ')
out=$(NO_COLOR=1 npx -y skills add . -l </dev/null 2>&1)
if echo "$out" | grep 'Skipped'; then fail=1; fi
if ! echo "$out" | grep -q "Found $want skills"; then
  echo "FAIL: the skills CLI did not find all $want skills"
  fail=1
fi
[ "$fail" -eq 0 ] && echo "check OK: $want skills install, all self-tests pass"
exit "$fail"
