#!/usr/bin/env python3
"""Auto-surface software-craft quotes from the orchestrator into data/quotes.json.

Hand-curated quotes (with their tags/context) are preserved; new sentences matching
craft-wisdom triggers are appended, de-duped by containment so split fragments of an
already-curated quote don't reappear.
"""
import json
import re
from pathlib import Path

PROJECT_DIR = Path.home() / ".claude/projects/-Users-stevendiamante-personal-rpg-combat"
EXCLUDED = {
    "9dfad67a-007a-4ea9-9045-e31490fb2d97",
    "9f3601c0-9816-4d07-829c-61a78b60ea5f",
    "a2b7f37b-9788-478e-85f0-93231a746334",
}
OUT = Path(__file__).resolve().parent.parent / "data" / "quotes.json"

TRIGGERS = {
    "make the change easy": "refactor-then-add · Kent Beck",
    "make it easy, then": "refactor-then-add · Kent Beck",
    "tidy first": "refactor-then-add · Kent Beck",
    "rule of three": "emergent design",
    "abstraction will emerge": "emergent design",
    "premature abstraction": "emergent design",
    "the duplication is": "clean code",
    "intention-reveal": "readable tests · Arlo Belshee",
    "carry the meaning": "readable tests · Arlo Belshee",
    "reads as a specification": "readable tests · Arlo Belshee",
    "triangulat": "TDD",
}

STATUS_RE = re.compile(r"^(behavior|launching|story\s+\d|all \d|now (story|behavior|i)|confirmed|marking|committed|split committed|done)\b", re.I)
NARR_RE = re.compile(r"^(i'll|i will|let me|let's|first|next|then i|now i)\b", re.I)

def looks_like_wisdom(s):
    if STATUS_RE.search(s) or NARR_RE.search(s):
        return False
    if "()" in s or re.search(r"\(\s*[,)]", s):  # leftover from stripped code
        return False
    return True

def overlaps(a, b):
    wa, wb = set(a.lower().split()), set(b.lower().split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / min(len(wa), len(wb))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def clean(sentence):
    s = re.sub(r"`[^`]*`", "", sentence)          # drop inline code
    s = re.sub(r"\s+", " ", s).strip(" -—*•")
    return s.strip()


def sentences(text):
    text = re.sub(r"\s+", " ", text)
    return re.split(r"(?<=[.!?])\s+(?=[A-Z\"`])", text)


def craft_tag(s):
    low = s.lower()
    for trig, tag in TRIGGERS.items():
        if trig in low:
            return tag
    return None


def main():
    existing = json.loads(OUT.read_text()) if OUT.exists() else []
    seen = [norm(q["text"]) for q in existing]
    added = 0
    for path in sorted(PROJECT_DIR.glob("*.jsonl")):
        if path.stem in EXCLUDED:
            continue
        for line in path.read_text().splitlines():
            if '"assistant"' not in line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "assistant" or row.get("isSidechain"):
                continue
            for b in row.get("message", {}).get("content", []):
                if not (isinstance(b, dict) and b.get("type") == "text"):
                    continue
                for raw in sentences(b.get("text", "")):
                    s = clean(raw)
                    tag = craft_tag(s)
                    if not tag or not (45 <= len(s) <= 300) or not looks_like_wisdom(s):
                        continue
                    n = norm(s)
                    if any(n in e or e in n for e in seen):
                        continue
                    if any(overlaps(s, q["text"]) >= 0.5 for q in existing):
                        continue
                    existing.append({"text": s, "context": "", "tag": tag, "auto": True})
                    seen.append(n)
                    added += 1
    OUT.write_text(json.dumps(existing, indent=2))
    print(f"quotes: {len(existing)} total (+{added} auto) -> {OUT}")


if __name__ == "__main__":
    main()
