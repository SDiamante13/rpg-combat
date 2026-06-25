#!/usr/bin/env python3
"""Per-turn context-window + output token usage for the orchestrator (data/usage.json)."""
import json
from pathlib import Path

PROJECT_DIR = Path.home() / ".claude/projects/-Users-stevendiamante-personal-rpg-combat"
EXCLUDED = {
    "9dfad67a-007a-4ea9-9045-e31490fb2d97",
    "9f3601c0-9816-4d07-829c-61a78b60ea5f",
    "a2b7f37b-9788-478e-85f0-93231a746334",
}
OUT = Path(__file__).resolve().parent.parent / "data" / "usage.json"


def main():
    turns = []
    seen_ids = set()
    for path in sorted(PROJECT_DIR.glob("*.jsonl")):
        if path.stem in EXCLUDED:
            continue
        for line in path.read_text().splitlines():
            if '"usage"' not in line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "assistant" or row.get("isSidechain"):
                continue
            mid = row.get("message", {}).get("id")
            if mid:
                if mid in seen_ids:
                    continue  # same message logged once per content block; count usage once
                seen_ids.add(mid)
            u = row.get("message", {}).get("usage")
            if not isinstance(u, dict):
                continue
            tin = u.get("input_tokens") or 0
            cw = u.get("cache_creation_input_tokens") or 0
            cr = u.get("cache_read_input_tokens") or 0
            out = u.get("output_tokens") or 0
            turns.append({
                "ts": row.get("timestamp"),
                "session": path.stem,
                "ctx": tin + cw + cr,
                "in": tin, "cw": cw, "cr": cr, "out": out,
            })
    turns.sort(key=lambda t: t["ts"] or "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(turns, indent=2))
    peak = max((t["ctx"] for t in turns), default=0)
    print(f"wrote {len(turns)} turns -> {OUT} (peak ctx {peak:,})")


if __name__ == "__main__":
    main()
