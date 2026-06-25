#!/usr/bin/env bash
# tdd-mark.sh — PreToolUse hook on the Skill tool. Writes a
# per-session marker when `tdd` is invoked. The companion
# `tdd-gate.sh` reads this marker to decide whether to allow
# Edit/Write/MultiEdit on code files.
#
# State is kept INSIDE the repo (.claude/.tdd-state) so the whole
# harness is self-contained and visible.
#
# Stdin: PreToolUse JSON payload (must include `session_id` and
#        `tool_input.skill`).
# Exit: 0 always — this hook never blocks; it only records state.

set -uo pipefail

PAYLOAD=""
if [ ! -t 0 ]; then
  PAYLOAD=$(cat 2>/dev/null || true)
fi

if [ -z "$PAYLOAD" ]; then
  exit 0
fi

MARKER_DIR="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/.tdd-state"
mkdir -p "$MARKER_DIR" 2>/dev/null || true

SKILL_NAME=$(printf '%s' "$PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('skill') or '')" 2>/dev/null || echo "")
SESSION_ID=$(printf '%s' "$PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id') or '')" 2>/dev/null || echo "")

if [ -z "$SKILL_NAME" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

case "$SKILL_NAME" in
  tdd)
    : > "$MARKER_DIR/$SESSION_ID" 2>/dev/null || true
    ;;
esac

exit 0
