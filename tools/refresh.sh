#!/usr/bin/env bash
# One loop tick: re-extract prompts, rebuild page, report any prompts still needing a label.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/extract_prompts.py >/dev/null
python3 tools/extract_delegations.py >/dev/null
python3 tools/extract_stories.py >/dev/null
python3 tools/extract_commits.py >/dev/null
python3 tools/extract_usage.py >/dev/null
python3 tools/extract_quotes.py >/dev/null
python3 tools/extract_metrics.py >/dev/null
python3 - <<'PY'
import json
prompts=json.load(open("data/prompts.json"))
labels=json.load(open("data/labels.json"))
missing=[p for p in prompts if p["ts"] not in labels]
print(f"{len(prompts)} prompts | {len(missing)} need labels")
for p in missing:
    print(f"  NEEDS LABEL {p['ts']} :: {p['display'][:80]}")
PY
python3 tools/build_page.py
