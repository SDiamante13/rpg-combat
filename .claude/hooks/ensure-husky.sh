#!/usr/bin/env bash
# ensure-husky.sh — PreToolUse hook on Bash. Before a `git commit`, make
# sure the Husky git hooks are actually installed, so the pre-commit
# `npm run checks` gate can't be silently skipped on a fresh clone (where
# .husky/_ and the local core.hooksPath are absent until `npm install`
# runs the `prepare` script).
#
# Cheap by design: it only runs `npm install` when the hooks are NOT yet
# wired; otherwise it exits immediately. Never blocks the commit.
#
# Stdin: PreToolUse JSON payload with `tool_input.command`.
# Exit: 0 always.

set -uo pipefail

PAYLOAD=""
if [ ! -t 0 ]; then
  PAYLOAD=$(cat 2>/dev/null || true)
fi
[ -z "$PAYLOAD" ] && exit 0

CMD=$(printf '%s' "$PAYLOAD" | python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('command') or '')" 2>/dev/null || echo "")

case "$CMD" in
  *"git commit"*) ;;
  *) exit 0 ;;
esac

DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
[ -f "$DIR/package.json" ] || exit 0

# Already wired? Husky v9 points core.hooksPath at .husky/_.
HOOKS_PATH=$(git -C "$DIR" config --local core.hooksPath 2>/dev/null || echo "")
if [ -n "$HOOKS_PATH" ] && [ -d "$DIR/$HOOKS_PATH" ]; then
  exit 0
fi

# Not wired — install dependencies; the `prepare` script runs husky and
# sets core.hooksPath. Output goes to stderr so it surfaces in the hook log.
( cd "$DIR" && npm install >&2 2>&1 ) || true
exit 0
