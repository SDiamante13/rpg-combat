#!/usr/bin/env python3
"""Merge prompts + delegations + labels into one self-contained role-aware index.html."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
prompts = json.loads((ROOT / "data" / "prompts.json").read_text())
delegs = json.loads((ROOT / "data" / "delegations.json").read_text())
labels = json.loads((ROOT / "data" / "labels.json").read_text())
commits_path = ROOT / "data" / "commits.json"
commits = json.loads(commits_path.read_text()) if commits_path.exists() else []
usage_path = ROOT / "data" / "usage.json"
usage_all = json.loads(usage_path.read_text()) if usage_path.exists() else []
quotes_path = ROOT / "data" / "quotes.json"
quotes = json.loads(quotes_path.read_text()) if quotes_path.exists() else []
metrics_path = ROOT / "data" / "metrics.json"
metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
fb = labels.get("_fallback", {"phase": "meta", "intent": "unknown", "summary": ""})

for p in prompts:
    p["role"] = "human"
    p["kind"] = p.get("kind", "prompt")

events = prompts + delegs
for e in events:
    lab = labels.get(e["ts"], {})
    e["phase"] = lab.get("phase") or ("green" if e["role"] == "subagent" else fb["phase"])
    e["intent"] = lab.get("intent") or ("implement-behavior" if e["role"] == "subagent" else fb["intent"])
    e["summary"] = lab.get("summary") or ("" if e["role"] == "human" else "")
    e["details"] = lab.get("details", [])
events = [e for e in events if not labels.get(e["ts"], {}).get("hide")]
events.sort(key=lambda e: e["ts"] or "")
for i, e in enumerate(events):
    e["i"] = i

import re
stories_path = ROOT / "data" / "stories.json"
stories = json.loads(stories_path.read_text()) if stories_path.exists() else {}
SUB_STORY = re.compile(r"\s*S(\d+)B")
cur_id, cur_title = "setup", "Setup & story splitting"
for e in events:  # already time-sorted; carry the active story forward
    if e["role"] == "subagent":
        m = SUB_STORY.match(e.get("task", ""))
        if m:
            n = m.group(1)
            cur_id, cur_title = f"story-{n}", stories.get(n, f"Story {n}")
    lab = labels.get(e["ts"], {})
    e["section_id"] = lab.get("section_id", cur_id)
    e["section_title"] = lab.get("section_title", cur_title)

from datetime import datetime
STOP = set("character feat test chore docs the a an to of from at and by up vs on in "
           "within target new starts cannot belongs makes its".split())

def _toks(text):
    t = re.sub(r"feat\([^)]*\):|test\([^)]*\):|chore:|docs:|\bS\d+B\d+\b", "", (text or "").lower())
    return {w for w in re.findall(r"[a-z0-9]+", t) if w not in STOP and len(w) > 1}

def _parse(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00"))

used = set()
for e in events:
    if e["role"] != "subagent":
        continue
    et, bt, best, bs = _parse(e["ts"]), _toks(e.get("task", "")), None, 0
    for c in commits:
        if c["sha"] in used or _parse(c["ts"]) < et:
            continue
        sc = len(bt & _toks(c["subject"]))
        if sc > bs or (sc == bs and sc > 0 and best and _parse(c["ts"]) < _parse(best["ts"])):
            bs, best = sc, c
    if best and bs >= 1:
        used.add(best["sha"])
        e["commit"] = {"short": best["short"], "subject": best["subject"], "url": best["url"]}

for e in events:  # explicit commit/option links from labels (e.g. human-directed refactors)
    lab = labels.get(e["ts"], {})
    e["option"] = lab.get("option")
    sha = lab.get("commit_sha")
    if sha and not e.get("commit"):
        c = next((c for c in commits if c["sha"].startswith(sha) or c["short"] == sha), None)
        if c:
            e["commit"] = {"short": c["short"], "subject": c["subject"], "url": c["url"]}

from collections import Counter
deleg_sessions = Counter(d.get("session") for d in delegs if d.get("session"))
orch_session = deleg_sessions.most_common(1)[0][0] if deleg_sessions else None
usage = [u for u in usage_all if u["session"] == orch_session]

data_json = json.dumps(events)
usage_json = json.dumps(usage)
quotes_json = json.dumps(quotes)

PR = {"in": 15.0, "cw": 18.75, "cr": 1.5, "out": 75.0}  # Opus standard $/MTok
orch_cost = sum(u["in"]*PR["in"] + u["cw"]*PR["cw"] + u["cr"]*PR["cr"] + u["out"]*PR["out"]
                for u in usage_all) / 1e6
subtok = sum(d.get("tokens") or 0 for d in delegs)
sub_cost = subtok / 1e6 * (0.965*PR["cr"] + 0.02*PR["out"] + 0.015*PR["cw"])
all_ts = [e["ts"] for e in events if e.get("ts")] + [u["ts"] for u in usage_all if u.get("ts")]
mins = 0
if all_ts:
    span = datetime.fromisoformat(max(all_ts).replace("Z", "+00:00")) - datetime.fromisoformat(min(all_ts).replace("Z", "+00:00"))
    mins = int(span.total_seconds() // 60)
stats = {"cost": round(orch_cost + sub_cost, 2), "mins": mins}
stats_json = json.dumps(stats)
metrics_json = json.dumps(metrics)

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>rpg-combat · a TDD-with-agents journey</title>
<style>
:root{
  --bg:#f6f8fa; --panel:#ffffff; --ink:#1a1f24; --muted:#57606a; --line:#d0d7de;
  --red:#cf222e; --green:#1a7f37; --refactor:#0969da; --spec:#9a6700; --meta:#656d76; --ops:#8250df; --rev:#bf3989;
  --sub:#0e8a8a; --sub-bg:#e9f7f7; --sub-border:#a6d9d9;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}

/* ── HEADER ── */
header{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.97);border-bottom:1px solid var(--line);padding:14px 20px;backdrop-filter:blur(8px)}
h1{margin:0;font-size:17px;font-weight:700;letter-spacing:-.2px}
.sub{color:var(--muted);font-size:13px;margin-top:3px}
.modelbar{display:flex;gap:7px;flex-wrap:wrap;margin-top:8px}
.mb{font-size:11.5px;font-weight:600;color:#1a1f24;background:#eef1f4;border:1px solid var(--line);border-radius:999px;padding:2px 10px}
.legend{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;font-size:12px}
.roles{display:flex;gap:12px;flex-wrap:wrap;margin-top:6px;font-size:12.5px;color:var(--muted)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
select,input{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:6px 10px;font-size:13px;transition:border-color .15s}
select:focus,input:focus{outline:2px solid #0969da55;border-color:#0969da;outline-offset:0}
input{flex:1;min-width:160px}

/* ── MAIN ── */
main{max-width:880px;margin:0 auto;padding:24px 18px 48px}

/* ── INTRO / EXPLAINER ── */
details.intro{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin-bottom:28px;overflow:hidden}
details.intro summary{cursor:pointer;font-weight:600;font-size:13.5px;list-style:none;display:flex;align-items:center;gap:7px;padding:13px 17px;user-select:none;color:var(--ink)}
details.intro summary::-webkit-details-marker{display:none}
details.intro summary::after{content:"▸";color:var(--muted);font-size:11px;margin-left:auto;transition:transform .18s}
details.intro[open] summary::after{transform:rotate(90deg)}
details.intro summary:hover{background:#f0f6ff}
.intro-body{padding:0 17px 15px;border-top:1px solid var(--line)}
.intro-body p{margin:12px 0 10px;font-size:13.5px;color:#2b3138;line-height:1.65;max-width:640px}
.role-grid{display:flex;flex-direction:column;gap:10px;margin-top:8px}
.role-item{display:flex;gap:11px;align-items:flex-start;font-size:13px;line-height:1.55}
.role-icon{font-size:20px;flex-shrink:0;line-height:1.2}
.role-label{font-weight:600;color:var(--ink)}
.role-desc{color:var(--muted);margin-top:1px;font-size:12.5px}

/* ── TURN STREAM ── */
.turn{margin:18px 0;display:flex;flex-direction:column;gap:5px}

/* Human → Orchestrator bubble (right-aligned) */
.bubble{max-width:76%;margin-left:auto;background:var(--panel);border:1px solid var(--line);border-right:4px solid var(--meta);border-radius:14px 14px 4px 14px;padding:13px 15px;box-shadow:0 1px 3px rgba(31,35,40,.07);transition:box-shadow .15s}
.bubble:hover{box-shadow:0 3px 9px rgba(31,35,40,.12)}
.bubble.cmd .text{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;color:#0550ae}
.meta-row{display:flex;gap:7px;align-items:center;justify-content:flex-end;margin-bottom:8px;font-size:11.5px;color:var(--muted);flex-wrap:wrap}
.tag{border:1px solid var(--line);border-radius:999px;padding:2px 9px;font-size:11px;font-weight:500}
.text{white-space:pre-wrap;word-break:break-word;line-height:1.6;font-size:14.5px}

/* Orchestrator summary (right-aligned block, text left-aligned) */
.orch{max-width:76%;margin-left:auto;color:#2b3138;font-size:13.5px;display:flex;gap:9px;align-items:flex-start;line-height:1.55}
.orch-icon{flex-shrink:0;font-size:15px;padding-top:2px}
.orch-body{flex:1;border-left:2px solid var(--line);padding-left:10px;text-align:left}

/* Orchestrator → SubAgent task card (left-aligned) */
.sub-card{max-width:72%;margin-right:auto;background:var(--sub-bg);border:1px solid var(--sub-border);border-left:4px solid var(--sub);border-radius:4px 14px 14px 14px;padding:12px 15px;box-shadow:0 1px 3px rgba(14,138,138,.08);transition:box-shadow .15s}
.sub-card:hover{box-shadow:0 3px 9px rgba(14,138,138,.18)}
.sub-head{display:flex;gap:7px;align-items:center;margin-bottom:8px;flex-wrap:wrap}
.sub-who{font-size:11px;color:var(--sub);font-weight:600}
.phase-chip{border-radius:999px;padding:2px 9px;font-size:11px;font-weight:700;color:#fff;letter-spacing:.03em}
.sub-time{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;margin-left:auto}
.sub-task{font-weight:700;font-size:14.5px;color:var(--ink);line-height:1.4;margin:0 0 7px}
.sub-ex{color:#37414a;font-size:12px;font-family:ui-monospace,Menlo,monospace;background:rgba(0,0,0,.05);border-radius:5px;padding:5px 8px;word-break:break-all;line-height:1.5}

.details{margin:8px 0 0;padding-left:16px;display:none}
.details.open{display:block}
.details li{margin:3px 0;font-size:12.5px;color:#2b3138;line-height:1.5}
.expand{cursor:pointer;opacity:.7;transition:opacity .15s}
.expand:hover{opacity:1}
.expand:focus-visible{outline:2px solid #0969da80;outline-offset:2px;border-radius:3px}
.time{font-variant-numeric:tabular-nums}
.empty{color:var(--muted);text-align:center;margin-top:40px;font-size:15px}



.commit{display:inline-flex;gap:7px;align-items:center;margin-top:3px;font-size:12.5px;color:var(--green);text-decoration:none;border:1px solid var(--sub-border);background:#fff;border-radius:7px;padding:5px 10px;line-height:1.45;max-width:100%}
.commit:hover{text-decoration:underline;border-color:var(--green)}
.commit .sha{font-family:ui-monospace,Menlo,monospace;font-weight:700;flex-shrink:0}
.commit .csub{color:#2b3138;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.commit.nocommit{color:#9a6700;border-color:#d4a72c;background:#fffbe6;border-style:dashed;cursor:default}

/* ── CRAFT QUOTES ── */
details.quotes{margin:0 0 22px;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
details.quotes>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;padding:13px 17px;font-size:11.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);font-weight:700;user-select:none}
details.quotes>summary::-webkit-details-marker{display:none}
details.quotes>summary::after{content:"\25B8";margin-left:auto;font-size:11px;transition:transform .18s}
details.quotes[open]>summary::after{transform:rotate(90deg)}
details.quotes>summary:hover{background:#f0f6ff}
.qcount{background:#f3eefe;color:var(--ops);border-radius:999px;padding:1px 8px;font-size:10.5px;font-weight:700;letter-spacing:0}
.qbody{padding:6px 17px 14px;border-top:1px solid var(--line)}
.quote{position:relative;background:linear-gradient(180deg,#faf8ff,#fff);border:1px solid #e6dcfb;border-left:4px solid var(--ops);border-radius:0 12px 12px 0;padding:15px 18px 14px 46px;margin:11px 0;box-shadow:0 1px 3px rgba(31,35,40,.06)}
.quote::before{content:"\201C";position:absolute;left:12px;top:6px;font-size:40px;line-height:1;color:#c4adf2;font-family:Georgia,serif}
.quote blockquote{margin:0;font-size:15.5px;line-height:1.55;color:var(--ink);font-style:italic}
.qmeta{margin-top:9px;font-size:12px;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.qtag{background:#f3eefe;color:var(--ops);border-radius:999px;padding:2px 10px;font-size:11px;font-weight:600;font-style:normal}

/* ── SECTIONS ── */
details.section{margin:14px 0;border:1px solid var(--line);border-radius:12px;background:#fbfcfd;overflow:hidden}
details.section>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:10px;padding:13px 16px;font-weight:700;font-size:14px;user-select:none;color:var(--ink)}
details.section>summary::-webkit-details-marker{display:none}
details.section>summary::before{content:"\25B8";color:var(--muted);font-size:12px;transition:transform .18s}
details.section[open]>summary::before{transform:rotate(90deg)}
details.section>summary:hover{background:#f0f6ff}
.sec-meta{margin-left:auto;font-weight:500;font-size:12px;color:var(--muted)}
.sec-body{padding:4px 22px 16px;border-top:1px solid var(--line)}

.chose{margin-top:8px;font-size:12.5px;font-weight:600;color:var(--green)}
.chose .x{font-weight:400;color:var(--muted)}
.sub-cost{margin-top:7px;font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
details.usage{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin-bottom:22px;overflow:hidden}
details.usage>summary{cursor:pointer;font-weight:700;font-size:13.5px;list-style:none;display:flex;align-items:center;gap:8px;padding:13px 17px;user-select:none}
details.usage>summary::-webkit-details-marker{display:none}
details.usage>summary::after{content:"\25B8";color:var(--muted);font-size:11px;margin-left:auto;transition:transform .18s}
details.usage[open]>summary::after{transform:rotate(90deg)}
details.usage>summary:hover{background:#f0f6ff}
.ubody{padding:4px 17px 16px;border-top:1px solid var(--line)}
.ustats{display:flex;flex-wrap:wrap;gap:14px 26px;margin:14px 0 4px}
.ustat{font-size:12.5px;color:var(--muted)}
.ustat b{display:block;font-size:18px;color:var(--ink);font-weight:700;font-variant-numeric:tabular-nums}
.usvg{width:100%;height:130px;margin-top:14px;display:block}
.uarea{fill:rgba(9,105,218,.10)}
.uline{fill:none;stroke:#0969da;stroke-width:1.5}
.compact{stroke:#cf222e;stroke-width:1.2;stroke-dasharray:3 2;opacity:.75}
.ulab{font-size:10.5px;fill:var(--muted)}
.estnote{font-size:10px;font-weight:500;color:var(--muted);font-style:italic}
.uhint{font-size:11.5px;color:var(--muted);margin-top:8px}
.uhint .ck{color:#cf222e;font-weight:600}

/* ── RESPONSIVE ── */
@media(max-width:640px){
  header{padding:11px 13px}
  h1{font-size:15px}
  .roles{font-size:11.5px}
  main{padding:16px 11px 100px}
  .bubble,.orch{max-width:92%}
  .sub-card{max-width:94%}
  .turn{margin:14px 0}
  select,input{font-size:14px;padding:7px 10px}
  .text{font-size:14px}
  .sub-task{font-size:14px}
}
</style></head><body>
<header>
  <h1>rpg-combat &middot; a TDD-with-agents journey</h1>
  <div class="sub" id="sub"></div>
  <div class="modelbar"><span class="mb">🧠 Claude Opus 4.8</span><span class="mb">⚡ effort: high</span><span class="mb">🪟 1M-token context</span></div>
  <div class="roles">🧑 you &rarr; 🧭 Orchestrator (your prompts, right) &nbsp;&middot;&nbsp; 🧭 &rarr; 👷 SubAgent (one behavior, left)</div>
  <div class="legend" id="legend"></div>
  <div class="controls">
    <select id="role"><option value="">all roles</option><option value="human">🧑 prompts</option><option value="subagent">👷 subagents</option></select>
    <select id="phase"><option value="">all phases</option></select>
    <input id="q" placeholder="search&hellip;">
  </div>
</header>
<main>
  <div id="panels"></div>
  <div id="stream"></div>
</main>

<script id="data" type="application/json">__DATA__</script>
<script id="usage" type="application/json">__USAGE__</script>
<script id="quotes" type="application/json">__QUOTES__</script>
<script id="stats" type="application/json">__STATS__</script>
<script id="metrics" type="application/json">__METRICS__</script>
<script>
const PHASES={red:"--red",green:"--green",refactor:"--refactor",spec:"--spec",meta:"--meta",ops:"--ops",review:"--rev"};
const EMOJI={red:"🔴",green:"🟢",refactor:"🔵",spec:"📋",meta:"⚙️",ops:"🔧",review:"🔍"};
const PHASE_BG={red:"#cf222e",green:"#1a7f37",refactor:"#0969da",spec:"#9a6700",meta:"#656d76",ops:"#8250df",review:"#bf3989"};
const DATA=JSON.parse(document.getElementById("data").textContent);
const USAGE=JSON.parse(document.getElementById("usage").textContent);
const kfmt=n=>!n?"0":n>=1000?(n/1000).toFixed(n>=10000?0:1)+"k":""+n;
const QUOTES=JSON.parse(document.getElementById("quotes").textContent);
const STATS=JSON.parse(document.getElementById("stats").textContent);
const METRICS=JSON.parse(document.getElementById("metrics").textContent);
const cssvar=p=>getComputedStyle(document.documentElement).getPropertyValue(PHASES[p]||"--meta");
const fmt=ts=>ts?new Date(ts).toLocaleTimeString("en-US",{hour:"2-digit",minute:"2-digit",timeZone:"America/New_York",timeZoneName:"short"}):"";
const esc=s=>(s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const phaseChip=p=>`<span class="phase-chip" style="background:${PHASE_BG[p]||"#656d76"}">${EMOJI[p]||""} ${p}</span>`;

function initHeader(){
  const c={};DATA.forEach(e=>c[e.phase]=(c[e.phase]||0)+1);
  document.getElementById("legend").innerHTML=Object.keys(PHASES).map(p=>
    `<span><span class="dot" style="background:${cssvar(p)}"></span>${EMOJI[p]} ${p} ${c[p]||0}</span>`).join("");
  const np=DATA.filter(e=>e.role==="human").length, ns=DATA.filter(e=>e.role==="subagent").length;
  document.getElementById("sub").innerHTML=`${np} prompts &middot; ${ns} subagent behaviors &nbsp;<span style="color:var(--muted);font-weight:400">// prompts verbatim &middot; agent work summarized</span>`;
  const ps=document.getElementById("phase");Object.keys(PHASES).forEach(p=>ps.add(new Option(`${EMOJI[p]} ${p}`,p)));
}

function introHTML(){
  return `<details class="intro" open>
  <summary>📖 How to read this page</summary>
  <div class="intro-body">
    <p>This is a verbatim record of one developer's prompts while building an RPG combat kata using Claude Code with strict outside-in TDD. Watch the three-role conversation unfold from first test to refactored code.</p>
    <div class="role-grid">
      <div class="role-item"><span class="role-icon">🧑</span><div><div class="role-label">You (the developer)</div><div class="role-desc">Raw prompts as typed — right-side bubbles, colored border = TDD phase. Commands (/) appear in monospace.</div></div></div>
      <div class="role-item"><span class="role-icon">🧭</span><div><div class="role-label">Orchestrator (Claude Code main loop)</div><div class="role-desc">Receives your prompt, decides which sub-behaviors to delegate. Summary appears under your bubble.</div></div></div>
      <div class="role-item"><span class="role-icon">👷</span><div><div class="role-label">SubAgent (one spawned behavior)</div><div class="role-desc">Left-side teal cards — each covers one red→green TDD cycle. The bold label is the behavior implemented. Phase chip shows TDD state.</div></div></div>
    </div>
  </div>
</details>`;
}

function detailsHTML(e){
  if(!e.details||!e.details.length)return"";
  return `<ul class="details">${e.details.map(d=>`<li>${esc(d)}</li>`).join("")}</ul>`;
}

function humanTurn(e){
  const col=cssvar(e.phase), det=detailsHTML(e);
  const opt=e.option?`<div class="chose">✅ chose: ${esc(e.option)}</div>`:"";
  const cmt=e.commit?`<a class="commit" href="${e.commit.url}" target="_blank" rel="noopener" title="${esc(e.commit.subject)}"><span class="sha">🔗 ${e.commit.short}</span><span class="csub">${esc(e.commit.subject)}</span></a>`:"";
  const orch=(e.summary||opt||cmt)?`<div class="orch">
    <span class="orch-icon">🧭</span>
    <div class="orch-body">
      <span class="expand" tabindex="0">${esc(e.summary)}${det?' ▾':''}</span>
      ${opt}${cmt}${det}
    </div>
  </div>`:"";
  return `<div class="turn">
    <div class="bubble ${e.kind==="command"?"cmd":""}" style="border-right-color:${col}">
      <div class="meta-row"><span class="tag">${EMOJI[e.phase]} ${e.phase}</span><span class="tag">${esc(e.intent)}</span><span class="time">🧑 ${fmt(e.ts)}</span></div>
      <div class="text">${esc(e.display)}</div>
    </div>${orch}</div>`;
}

function subTurn(e){
  const det=detailsHTML(e);
  return `<div class="turn">
    <div class="sub-card">
      <div class="sub-head">
        <span class="sub-who">🧭 &rarr; 👷 ${esc(e.agent_type||"claude")}</span>
        ${phaseChip(e.phase)}
        <span class="sub-time">${fmt(e.ts)}</span>
      </div>
      <div class="sub-task expand" tabindex="0">${esc(e.task)}${det?' <span class="expand">▾</span>':''}</div>
      ${(e.tokens||e.tools||e.ms)?`<div class="sub-cost">🪙 ${kfmt(e.tokens||0)} tokens${e.tools?` &middot; 🔧 ${e.tools} tools`:""}${e.ms?` &middot; ⏱ ${Math.round(e.ms/1000)}s`:""}</div>`:""}
      ${e.commit?`<a class="commit" href="${e.commit.url}" target="_blank" rel="noopener" title="${esc(e.commit.subject)}"><span class="sha">🔗 ${e.commit.short}</span><span class="csub">${esc(e.commit.subject)}</span></a>`:`<span class="commit nocommit">⏳ commit pending</span>`}
      ${det}
    </div></div>`;
}

function usageChart(){
  if(USAGE.length<2)return"";
  const W=840,H=130,pad=30,maxC=Math.max(...USAGE.map(u=>u.ctx))||1;
  const x=i=>pad+(W-2*pad)*(i/(USAGE.length-1));
  const y=c=>H-20-(H-40)*(c/maxC);
  let line="M"+x(0).toFixed(1)+" "+y(USAGE[0].ctx).toFixed(1);
  USAGE.forEach((u,i)=>{if(i)line+=" L"+x(i).toFixed(1)+" "+y(u.ctx).toFixed(1);});
  const area=line+" L"+x(USAGE.length-1).toFixed(1)+" "+(H-20)+" L"+x(0).toFixed(1)+" "+(H-20)+" Z";
  let marks="",ncomp=0;
  for(let i=1;i<USAGE.length;i++){if(USAGE[i-1].ctx-USAGE[i].ctx>30000){ncomp++;marks+=`<line x1="${x(i).toFixed(1)}" y1="6" x2="${x(i).toFixed(1)}" y2="${H-20}" class="compact"/>`;}}
  return `<svg viewBox="0 0 ${W} ${H}" class="usvg" preserveAspectRatio="none"><path d="${area}" class="uarea"/><path d="${line}" class="uline"/>${marks}<text x="${pad}" y="13" class="ulab">orchestrator context per turn &middot; peak ${kfmt(maxC)} (${(maxC/1e6*100).toFixed(1)}% of 1M)</text></svg>`
    +`<div class="uhint">${ncomp?`<span class="ck">red dashed</span> = context compaction (${ncomp})`:"no compactions yet"}</div>`;
}
function quotesPanel(){
  if(!QUOTES.length)return"";
  return `<details class="usage" open><summary>💬 Craft notes &mdash; in the orchestrator&rsquo;s words</summary><div class="ubody"><section class="quotes">${
    QUOTES.map(q=>`<div class="quote"><blockquote>${esc(q.text)}</blockquote><div class="qmeta">${q.tag?`<span class="qtag">${esc(q.tag)}</span>`:""}${q.context?`<span>${esc(q.context)}</span>`:""}</div></div>`).join("")
  }</section></div></details>`;
}
function metricsPanel(){
  const m=METRICS; if(!m||!m.prod)return"";
  const row=(label,val)=>`<div class="ustat"><b>${val}</b>${label}</div>`;
  return `<details class="usage" open><summary>📐 Code metrics &middot; main branch</summary><div class="ubody">
    <div class="ustats">
      ${row("prod LOC / file", m.prod.loc_per_file)}
      ${row("prod LOC / function", m.prod.loc_per_fn)}
      ${row("test LOC / file", m.test.loc_per_file)}
      ${row("test LOC / function", m.test.loc_per_fn)}
      ${row("test : prod LOC", m.test_prod_ratio+":1")}
    </div>
    <div class="ustats" style="margin-top:6px">
      ${row("test cases", m.tests)}
      ${row("tests / behavior", m.tests_per_behavior)}
      ${row("comment density", m.comment_density+"%")}
      ${row("methods / class", m.methods_per_class)}
      ${row("commits", m.commits+" / "+m.behaviors+" behaviors")}
    </div>
    <div class="uhint">${m.refactors} dedicated refactor commits &middot; every function under the 10-line eslint cap</div>
  </div></details>`;
}
function usagePanel(){
  const subs=DATA.filter(e=>e.role==="subagent");
  const tok=subs.reduce((s,e)=>s+(e.tokens||0),0), nb=subs.length;
  const peak=Math.max(...USAGE.map(u=>u.ctx),0);
  const out=USAGE.reduce((s,u)=>s+u.out,0);
  return `<details class="usage" open><summary>📊 Token &amp; context usage</summary><div class="ubody">
    <div class="ustats">
      <div class="ustat"><b>${kfmt(tok)}</b>subagent tokens</div>
      <div class="ustat"><b>${nb}</b>behaviors</div>
      <div class="ustat"><b>${kfmt(nb?tok/nb:0)}</b>avg / behavior</div>
      <div class="ustat"><b>${kfmt(peak)}</b>peak context (${(peak/1e6*100).toFixed(1)}% of 1M)</div>
      <div class="ustat"><b>${kfmt(out)}</b>orchestrator output</div>
      <div class="ustat"><b>~$${(STATS.cost||0).toFixed(2)}</b>est. cost <span class="estnote">token-based</span></div>
      <div class="ustat"><b>${Math.floor((STATS.mins||0)/60)}h ${(STATS.mins||0)%60}m</b>total time</div>
    </div>${usageChart()}</div></details>`;
}
function turnHTML(e){return e.role==="subagent"?subTurn(e):humanTurn(e);}
function sectionsHTML(rows){
  const filtering=document.getElementById("role").value||document.getElementById("phase").value||document.getElementById("q").value;
  const order=[],groups={};
  rows.forEach(e=>{const id=e.section_id||"setup";if(!groups[id]){groups[id]={title:e.section_title||id,items:[]};order.push(id);}groups[id].items.push(e);});
  return order.map(id=>{
    const g=groups[id];
    const np=g.items.filter(e=>e.role==="human").length,ns=g.items.filter(e=>e.role==="subagent").length;
    const meta=[np?`${np} prompt${np>1?"s":""}`:"",ns?`${ns} behavior${ns>1?"s":""}`:""].filter(Boolean).join(" \u00b7 ");
    const open=" open";
    return `<details class="section"${open}><summary><span>${esc(g.title)}</span><span class="sec-meta">${meta}</span></summary><div class="sec-body">${g.items.map(turnHTML).join("")}</div></details>`;
  }).join("");
}
function renderPanels(){
  document.getElementById("panels").innerHTML=introHTML()+quotesPanel()+usagePanel()+metricsPanel();
}
function applyPanelState(){
  const filtering=document.getElementById("role").value||document.getElementById("phase").value||document.getElementById("q").value;
  document.querySelectorAll("#panels > details").forEach(d=>{d.open=!filtering;});
}
function render(){
  const fr=document.getElementById("role").value,
        fp=document.getElementById("phase").value,
        q=document.getElementById("q").value.toLowerCase();
  const rows=DATA.filter(e=>
    (!fr||e.role===fr)&&(!fp||e.phase===fp)&&
    (!q||((e.display||e.task||"")+" "+(e.excerpt||"")).toLowerCase().includes(q)));
  applyPanelState();
  const m=document.getElementById("stream");
  if(!rows.length){m.innerHTML='<div class="empty">nothing matches.</div>';return;}
  m.innerHTML=sectionsHTML(rows);
  m.querySelectorAll(".expand").forEach(x=>x.addEventListener("click",()=>{
    const d=x.closest(".turn").querySelector(".details");if(d)d.classList.toggle("open");
  }));
  m.querySelectorAll(".expand[tabindex]").forEach(x=>x.addEventListener("keydown",ev=>{
    if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();x.click();}
  }));
}

initHeader();renderPanels();render();
["role","phase","q"].forEach(id=>document.getElementById(id).addEventListener("input",render));
</script>
</body></html>"""

html = (HTML.replace("__DATA__", data_json).replace("__USAGE__", usage_json)
        .replace("__QUOTES__", quotes_json).replace("__STATS__", stats_json)
        .replace("__METRICS__", metrics_json))
html = re.sub(r"/Users/[A-Za-z0-9._-]+", "~", html)  # scrub home/username paths
(ROOT / "index.html").write_text(html)
print(f"built index.html · {len(prompts)} prompts + {len(delegs)} delegations")
