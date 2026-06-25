#!/usr/bin/env bash
# tdd-gate.sh — PreToolUse hook on Edit/Write/MultiEdit. Denies
# the tool call when the target is a code file AND the `tdd` skill
# has not been loaded this session (no marker written by tdd-mark.sh).
#
# Rationale: every code-file edit must trace to a failing test, per the
# tdd discipline. Loading the skill is a precondition; the skill's
# content reminds the model of the RGR/hardcode-first rules.
#
# State is kept INSIDE the repo (.claude/.tdd-state) so the whole
# harness is self-contained and visible.
#
# Bypass: set `SKIP_TDD_GATE=1` in the environment to skip the gate
# for a session (e.g. emergency hotfix). The bypass is per-process,
# so it disappears the moment the shell exits.
#
# Stdin: PreToolUse JSON payload with `tool_name`, `tool_input`
#        (containing `file_path`), and `session_id`.
# Output: JSON deny payload when the gate fires. Empty (exit 0) otherwise.

set -uo pipefail

if [ "${SKIP_TDD_GATE:-}" = "1" ]; then
  exit 0
fi

PAYLOAD=""
if [ ! -t 0 ]; then
  PAYLOAD=$(cat 2>/dev/null || true)
fi

if [ -z "$PAYLOAD" ]; then
  exit 0
fi

MARKER_DIR="${CLAUDE_PROJECT_DIR:-$PWD}/.claude/.tdd-state"

FILE_PATH=$(printf '%s' "$PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path') or '')" 2>/dev/null || echo "")
SESSION_ID=$(printf '%s' "$PAYLOAD" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('session_id') or '')" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ] || [ -z "$SESSION_ID" ]; then
  exit 0
fi

# Exempt paths — harness internals, vendored code, build output,
# fixtures, declaration files. Not the "production code" the gate protects.
case "$FILE_PATH" in
  */.claude/* | */skills/* | */node_modules/* | */dist/* | */build/* | */coverage/* | */__fixtures__/* | */target/* | */.next/* | */.venv/*)
    exit 0
    ;;
  *.d.ts)
    exit 0
    ;;
  *.config.js | *.config.ts | *.config.mjs | *.config.cjs)
    exit 0
    ;;
esac

# Code-file extension check. Anything not listed is allowed without the gate.
case "$FILE_PATH" in
  *.ts | *.tsx | *.mts | *.cts | \
  *.js | *.jsx | *.mjs | *.cjs | \
  *.py | *.java | *.rb | *.go | *.rs | \
  *.kt | *.swift | *.scala | \
  *.c | *.cc | *.cpp | *.cxx | *.h | *.hh | *.hpp | *.hxx | \
  *.cs | *.m | *.mm)
    ;;
  *)
    exit 0
    ;;
esac

if [ -f "$MARKER_DIR/$SESSION_ID" ]; then
  exit 0
fi

REASON="TDD gate: invoke /tdd before editing code (target: $FILE_PATH).

The tdd skill enforces the red-green-refactor discipline this codebase relies on:
- ONE failing test per turn (no speculative batches)
- Run the test, see it RED, then minimum code to make it GREEN
- Hardcode first; generalize only when triangulation demands it

Invoke /tdd via the Skill tool now, then retry the edit. Emergency bypass: set SKIP_TDD_GATE=1 in the environment (use sparingly — it leaves no audit trail)."

REASON_ESCAPED=$(REASON_TEXT="$REASON" python3 -c "import json,os; print(json.dumps(os.environ['REASON_TEXT']))")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": $REASON_ESCAPED
  }
}
EOF

exit 0
