#!/usr/bin/env bash
# Restore your personal harness after a research run (reverses demo-isolate.sh).
set -euo pipefail

CLAUDE_HOME="$HOME/.claude"
STAMP="demo-isolate"

if [ -d "$CLAUDE_HOME/skills.$STAMP.bak" ]; then
  rm -rf "$CLAUDE_HOME/skills.isolated.tmp" 2>/dev/null || true
  [ -d "$CLAUDE_HOME/skills" ] && mv "$CLAUDE_HOME/skills" "$CLAUDE_HOME/skills.isolated.tmp"
  mv "$CLAUDE_HOME/skills.$STAMP.bak" "$CLAUDE_HOME/skills"
  rm -rf "$CLAUDE_HOME/skills.isolated.tmp" 2>/dev/null || true
  echo "restored ~/.claude/skills"
else
  echo "no skills backup found — skipping"
fi

if [ -f "$CLAUDE_HOME/settings.json.$STAMP.bak" ]; then
  mv "$CLAUDE_HOME/settings.json.$STAMP.bak" "$CLAUDE_HOME/settings.json"
  echo "restored root settings.json (plugins re-enabled)"
else
  echo "no settings backup found — skipping"
fi

echo "DONE. Relaunch claude to pick up your full harness again."
