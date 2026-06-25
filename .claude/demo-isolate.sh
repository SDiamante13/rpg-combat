#!/usr/bin/env bash
# Isolate the agent harness to ONLY this repo's skills for a research run.
# Moves your personal skills aside and disables global plugins, backing up
# root settings.json first. Reverse with demo-restore.sh.
#
# Run this, then RELAUNCH claude in this repo so discovery re-runs.
set -euo pipefail

CLAUDE_HOME="$HOME/.claude"
STAMP="demo-isolate"

if [ -d "$CLAUDE_HOME/skills" ] && [ ! -d "$CLAUDE_HOME/skills.$STAMP.bak" ]; then
  mv "$CLAUDE_HOME/skills" "$CLAUDE_HOME/skills.$STAMP.bak"
  echo "moved ~/.claude/skills -> skills.$STAMP.bak"
else
  echo "skills already isolated (or missing) — skipping"
fi

if [ -f "$CLAUDE_HOME/settings.json" ] && [ ! -f "$CLAUDE_HOME/settings.json.$STAMP.bak" ]; then
  cp "$CLAUDE_HOME/settings.json" "$CLAUDE_HOME/settings.json.$STAMP.bak"
  python3 - "$CLAUDE_HOME/settings.json" <<'PY'
import json,sys
p=sys.argv[1]
d=json.load(open(p))
d["enabledPlugins"]={k:False for k in d.get("enabledPlugins",{})}
# Neutralize global hooks (rtk-rewrite, tdd-mark, tdd-gate) so only this
# repo's .claude/settings.json hooks run during the demo.
d["hooks"]={}
json.dump(d,open(p,"w"),indent=2)
PY
  echo "disabled global plugins + cleared global hooks in root settings.json (backup saved)"
else
  echo "root settings backup already exists — skipping plugin/hook toggle"
fi

echo "DONE. Relaunch claude in this repo. Restore with: bash .claude/demo-restore.sh"
