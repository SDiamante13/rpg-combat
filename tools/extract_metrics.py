#!/usr/bin/env python3
"""Code metrics on the kata's main source (data/metrics.json)."""
import re, glob, subprocess, json
from pathlib import Path

KATA = "/Users/stevendiamante/personal/rpg-combat"
OUT = Path(__file__).resolve().parent.parent / "data" / "metrics.json"
KW = {"if", "for", "while", "switch", "catch", "return", "else", "do", "function"}
SIG = re.compile(r"^\s*(?:export\s+)?(?:public|private|protected|static|async|get|set|readonly|\s)*([A-Za-z_]\w*)\s*\([^)]*\)\s*(?::[^={]+)?\{")
ARROW = re.compile(r"=>\s*\{")
TEST = re.compile(r"\b(it|test)\s*\(")


def code_lines(t):
    out, blk = [], False
    for ln in t.splitlines():
        s = ln.strip()
        if not s:
            continue
        if blk:
            blk = "*/" not in s
            continue
        if s.startswith("//"):
            continue
        if s.startswith("/*"):
            blk = "*/" not in s
            continue
        out.append(ln)
    return out


def comment_count(t):
    return sum(1 for ln in t.splitlines()
               if ln.strip().startswith(("//", "/*", "*")))


def count_fns(t):
    n = 0
    for ln in t.splitlines():
        m = SIG.match(ln)
        if m and m.group(1) not in KW:
            n += 1
        elif ARROW.search(ln):
            n += 1
    return n


def agg(group):
    code = fn = cmt = 0
    for f in group:
        t = open(f).read()
        code += len(code_lines(t)); fn += count_fns(t); cmt += comment_count(t)
    return {"files": len(group), "loc": code, "fns": fn,
            "loc_per_file": round(code / len(group), 1) if group else 0,
            "loc_per_fn": round(code / fn, 1) if fn else 0, "comments": cmt}


def main():
    files = [f for f in sorted(glob.glob(f"{KATA}/src/**/*.ts", recursive=True))
             if not f.endswith("index.ts")]
    prod = [f for f in files if not f.endswith(".test.ts")]
    test = [f for f in files if f.endswith(".test.ts")]
    P, T = agg(prod), agg(test)
    ntests = sum(len(TEST.findall(open(f).read())) for f in test)
    classes = sum(len(re.findall(r"\bclass\s+\w+", open(f).read())) for f in prod)
    log = subprocess.check_output(["git", "-C", KATA, "log", "--pretty=%s"], text=True).splitlines()
    feat = [l for l in log if l.startswith("feat") or l.startswith("test(")]
    refac = [l for l in log if l.startswith(". t") or "refactor" in l]
    data = {
        "prod": P, "test": T, "tests": ntests, "classes": classes,
        "methods_per_class": round(P["fns"] / classes, 1) if classes else 0,
        "test_prod_ratio": round(T["loc"] / P["loc"], 2) if P["loc"] else 0,
        "tests_per_behavior": round(ntests / len(feat), 1) if feat else 0,
        "comment_density": round(100 * P["comments"] / (P["loc"] + P["comments"]), 1) if P["loc"] else 0,
        "commits": len(log), "behaviors": len(feat), "refactors": len(refac),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2))
    print(f"metrics -> {OUT}: {data['prod']['loc_per_fn']} prod LOC/fn, {ntests} tests, {data['comment_density']}% comments")


if __name__ == "__main__":
    main()
