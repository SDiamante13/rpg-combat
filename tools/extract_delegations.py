#!/usr/bin/env python3
"""Extract orchestrator -> subagent delegations (Agent tool calls) + their token cost.

Each delegation is one behavior handed to a subagent (its own red-green-refactor
cycle). We surface the task label and the subagent's token/tool/duration totals.
"""
import json
from pathlib import Path

PROJECT_DIR = Path.home() / ".claude/projects/-Users-stevendiamante-personal-rpg-combat"
EXCLUDED_SESSIONS = {
    "9dfad67a-007a-4ea9-9045-e31490fb2d97",  # harness / skills setup
    "9f3601c0-9816-4d07-829c-61a78b60ea5f",  # meta viz-building session
    "a2b7f37b-9788-478e-85f0-93231a746334",  # page-polish subagent session
}
OUT = Path(__file__).resolve().parent.parent / "data" / "delegations.json"


def result_meta(rows):
    """Map tool_use_id -> {tokens, ms, tools} from Agent tool_result rows."""
    meta = {}
    for row in rows:
        tur = row.get("toolUseResult")
        if not isinstance(tur, dict) or "totalTokens" not in tur:
            continue
        for b in row.get("message", {}).get("content", []):
            if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("tool_use_id"):
                meta[b["tool_use_id"]] = {
                    "tokens": tur.get("totalTokens"),
                    "ms": tur.get("totalDurationMs"),
                    "tools": tur.get("totalToolUseCount"),
                }
    return meta


def extract_session(path):
    rows = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    meta = result_meta(rows)
    out = []
    for row in rows:
        if row.get("type") != "assistant" or row.get("isSidechain"):
            continue
        for block in row.get("message", {}).get("content", []):
            if not (isinstance(block, dict) and block.get("type") == "tool_use"
                    and block.get("name") == "Agent"):
                continue
            inp = block.get("input", {})
            m = meta.get(block.get("id"), {})
            out.append({
                "ts": row.get("timestamp"),
                "session": path.stem,
                "role": "subagent",
                "kind": "delegation",
                "task": inp.get("description") or inp.get("name") or "subagent task",
                "agent_type": inp.get("subagent_type", "claude"),
                "tokens": m.get("tokens"),
                "ms": m.get("ms"),
                "tools": m.get("tools"),
            })
    return out


def main():
    dels = []
    for path in sorted(PROJECT_DIR.glob("*.jsonl")):
        if path.stem in EXCLUDED_SESSIONS:
            continue
        dels.extend(extract_session(path))
    dels.sort(key=lambda d: d["ts"] or "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dels, indent=2))
    total = sum(d["tokens"] or 0 for d in dels)
    print(f"wrote {len(dels)} delegations ({total:,} subagent tokens) -> {OUT}")


if __name__ == "__main__":
    main()
