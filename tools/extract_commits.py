#!/usr/bin/env python3
"""Read the kata repo's commits into data/commits.json (sha, ts, subject, url)."""
import json
import re
import subprocess
from pathlib import Path

KATA = "/Users/stevendiamante/personal/rpg-combat"
OUT = Path(__file__).resolve().parent.parent / "data" / "commits.json"


def remote_url():
    try:
        url = subprocess.check_output(["git", "-C", KATA, "remote", "get-url", "origin"], text=True).strip()
    except subprocess.CalledProcessError:
        return None
    m = re.search(r"github\.com[:/](.+?)(?:\.git)?$", url)
    return f"https://github.com/{m.group(1)}" if m else None


def main():
    base = remote_url()
    log = subprocess.check_output(
        ["git", "-C", KATA, "log", "--pretty=format:%H%x1f%cI%x1f%s"], text=True)
    commits = []
    for line in log.splitlines():
        sha, ts, subject = line.split("\x1f")
        commits.append({
            "sha": sha, "short": sha[:7], "ts": ts, "subject": subject,
            "url": f"{base}/commit/{sha}" if base else None,
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(commits, indent=2))
    print(f"wrote {len(commits)} commits -> {OUT}")


if __name__ == "__main__":
    main()
