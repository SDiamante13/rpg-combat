#!/usr/bin/env python3
"""Map story number -> title from the orchestrator's TaskCreate calls (data/stories.json)."""
import json
import re
from pathlib import Path

PROJECT_DIR = Path.home() / ".claude/projects/-Users-stevendiamante-personal-rpg-combat"
EXCLUDED = {
    "9dfad67a-007a-4ea9-9045-e31490fb2d97",
    "9f3601c0-9816-4d07-829c-61a78b60ea5f",
    "a2b7f37b-9788-478e-85f0-93231a746334",
}
OUT = Path(__file__).resolve().parent.parent / "data" / "stories.json"
STORY_RE = re.compile(r"Story\s+(\d+)")


def main():
    stories = {}
    for path in sorted(PROJECT_DIR.glob("*.jsonl")):
        if path.stem in EXCLUDED:
            continue
        for line in path.read_text().splitlines():
            if '"TaskCreate"' not in line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "assistant" or row.get("isSidechain"):
                continue
            for b in row.get("message", {}).get("content", []):
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "TaskCreate":
                    subject = (b.get("input", {}) or {}).get("subject", "")
                    m = STORY_RE.search(subject)
                    if m:
                        stories[m.group(1)] = subject.strip()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(stories, indent=2))
    print(f"wrote {len(stories)} stories -> {OUT}")
    for n, t in sorted(stories.items()):
        print(f"  {n}: {t}")


if __name__ == "__main__":
    main()
