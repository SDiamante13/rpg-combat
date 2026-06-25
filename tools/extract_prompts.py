#!/usr/bin/env python3
"""Extract the prompts a human actually typed to Claude Code, for the TDD journey viz.

Iterates user messages (reliable timestamps + ordering), drops the harness-setup
session and interruption markers, and collapses skill-expanded slash commands back
to the terse `/<skill> <args>` the human really typed.
"""
import json
import re
from pathlib import Path

PROJECT_DIR = Path.home() / ".claude/projects/-Users-stevendiamante-personal-rpg-combat"
EXCLUDED_SESSIONS = {
    "9dfad67a-007a-4ea9-9045-e31490fb2d97",  # harness / skills setup
    "9f3601c0-9816-4d07-829c-61a78b60ea5f",  # this meta viz-building session
    "a2b7f37b-9788-478e-85f0-93231a746334",  # page-polish subagent session
}
OUT = Path(__file__).resolve().parent.parent / "data" / "prompts.json"

SKILL_RE = re.compile(r"Base directory for this skill:\s*\S*/skills/([\w-]+)")
ARGS_RE = re.compile(r"\nARGUMENTS:\s*(.*)\Z", re.S)
NOISE = re.compile(r"^\s*(\[Request interrupted by user|<(system-reminder|command-|local-command|teammate-message)|Caveat:|Shell cwd was reset|# /loop\b)|Parse the input below into", re.I)


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def classify(text):
    """Return (kind, display, command, body). Collapse skill expansions to /cmd args."""
    skill = SKILL_RE.search(text)
    if skill:
        name = skill.group(1)
        args = ARGS_RE.search(text)
        tail = (" " + args.group(1).strip()) if args and args.group(1).strip() else ""
        return "command", f"/{name}{tail}", name, text.strip()
    return "prompt", text.strip(), None, None


def is_noise(text):
    t = text.strip()
    if not t:
        return True
    if NOISE.search(t):
        return True
    return t.startswith("<") and "</" in t[:60]


def is_subagent_session(path):
    """A spawned-agent transcript: first human message is a 'You are ...' task prompt
    (often wrapped in a <teammate-message> envelope)."""
    for line in path.read_text().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("type") != "user" or row.get("message", {}).get("role") != "user":
            continue
        raw = text_of(row["message"].get("content"))
        raw = re.sub(r"</?teammate-message[^>]*>", "", raw).strip()
        if not raw:
            continue
        return raw.lower().startswith("you are ")
    return False


def extract_session(path):
    out = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("type") != "user":
            continue
        msg = row.get("message", {})
        if msg.get("role") != "user":
            continue
        if row.get("isSidechain"):
            continue  # subagent turn, not human-typed
        text = text_of(msg.get("content"))
        if is_noise(text):
            continue
        kind, display, command, body = classify(text)
        out.append({
            "session": path.stem,
            "ts": row.get("timestamp"),
            "kind": kind,
            "command": command,
            "display": display,
            "body": body,
            "chars": len(display),
        })
    return out


def main():
    prompts = []
    for path in sorted(PROJECT_DIR.glob("*.jsonl")):
        if path.stem in EXCLUDED_SESSIONS or is_subagent_session(path):
            continue
        prompts.extend(extract_session(path))
    prompts.sort(key=lambda p: p["ts"] or "")
    for i, p in enumerate(prompts):
        p["index"] = i
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(prompts, indent=2))
    print(f"wrote {len(prompts)} prompts -> {OUT}")
    for p in prompts:
        print(f"  [{p['kind'][:3]}] {p['display'][:70]}")


if __name__ == "__main__":
    main()
