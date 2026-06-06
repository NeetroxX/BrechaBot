from __future__ import annotations

import html as _html
import math

from ..models import Finding

# --- semantic palette (dark console theme) -------------------------------------------------
_SEV = {
    "high": "#ff4d6d",
    "medium": "#ffb020",
    "low": "#ffd24d",
    "none": "#2ee6a6",
}
_VERDICT = {
    "VULNERABLE": "#ff4d6d",
    "PARTIAL": "#ffb020",
    "SAFE": "#2ee6a6",
    "UNKNOWN": "#8b8a9c",
    "ERROR": "#8b8a9c",
}


def _esc(value: object) -> str:
    return _html.escape("" if value is None else str(value))


def _sev_color(severity: str) -> str:
    return _SEV.get(severity, "#8b8a9c")


def _verdict_color(verdict: str) -> str:
    return _VERDICT.get(verdict, "#8b8a9c")


def _grade_color(score: int) -> str:
    if score >= 80:
        return "#2ee6a6"
    if score >= 60:
        return "#ffb020"
    return "#ff4d6d"


# --- components ----------------------------------------------------------------------------
def _score_ring(score: int, grade: str) -> str:
    color = _grade_color(score)
    r = 78
    circ = 2 * math.pi * r
    dash = circ * (score / 100)
    return f"""
    <div class="ring-wrap">
      <svg viewBox="0 0 200 200" class="ring">
        <defs>
          <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{color}"/>
            <stop offset="100%" stop-color="{color}" stop-opacity="0.45"/>
          </linearGradient>
        </defs>
        <circle cx="100" cy="100" r="{r}" class="ring-track"/>
        <circle cx="100" cy="100" r="{r}" class="ring-fill"
                stroke="url(#ringGrad)"
                stroke-dasharray="{dash:.2f} {circ:.2f}"
                transform="rotate(-90 100 100)"/>
      </svg>
      <div class="ring-center">
        <div class="ring-grade" style="color:{color}">{_esc(grade)}</div>
        <div class="ring-score">{score}<span>/100</span></div>
        <div class="ring-label">RESILIENCE</div>
      </div>
    </div>"""


def _kpi(label: str, value: int, color: str, hint: str) -> str:
    return f"""
    <div class="kpi" style="--c:{color}">
      <div class="kpi-dot"></div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-label">{_esc(label)}</div>
      <div class="kpi-hint">{_esc(hint)}</div>
    </div>"""


def _owasp_bars(by_owasp: dict[str, dict[str, int]]) -> str:
    rows = sorted(by_owasp.items(), key=lambda kv: (-kv[1]["vulnerable"], -kv[1]["total"]))
    if not rows:
        return '<div class="empty">No OWASP categories were exercised in this scan.</div>'
    max_total = max(v["total"] for _, v in rows) or 1
    out = []
    for key, val in rows:
        total = val["total"]
        vuln = val["vulnerable"]
        width = total / max_total * 100
        vuln_pct = (vuln / total * 100) if total else 0
        status = "danger" if vuln else "clean"
        out.append(f"""
      <div class="bar-row {status}">
        <div class="bar-label" title="{_esc(key)}">{_esc(key)}</div>
        <div class="bar-track" style="width:{width:.1f}%">
          <div class="bar-vuln" style="width:{vuln_pct:.1f}%"></div>
        </div>
        <div class="bar-count">
          <span class="c-vuln">{vuln}</span><span class="c-sep">/</span><span class="c-total">{total}</span>
        </div>
      </div>""")
    return "".join(out)


def _badges(f: Finding) -> str:
    b = []
    if f.lang and f.lang != "en":
        b.append(f'<span class="badge badge-lang">{_esc(f.lang.upper())}</span>')
    if f.is_multi_turn:
        b.append('<span class="badge badge-mt">MULTI-TURN</span>')
    return "".join(b)


def _transcript(f: Finding) -> str:
    turns = []
    for turn in f.transcript:
        turns.append(f"""
        <div class="turn">
          <div class="turn-head"><span class="turn-no">{turn.turn:02d}</span> ATTACKER</div>
          <div class="msg msg-atk">{_esc(turn.user[:600])}</div>
          <div class="turn-head bot"><span class="turn-no">{turn.turn:02d}</span> BOT</div>
          <div class="msg msg-bot">{_esc(turn.bot[:600])}</div>
        </div>""")
    return "".join(turns)


def _finding_cards(findings: list[Finding]) -> str:
    weight = {"high": 3, "medium": 2, "low": 1, "none": 0}
    ordered = sorted(findings, key=lambda f: -weight.get(f.severity.value, 0))
    cards = []
    for i, f in enumerate(ordered):
        v = f.verdict.value
        vc = _verdict_color(v)
        sc = _sev_color(f.severity.value)
        remediation = ""
        if v in ("VULNERABLE", "PARTIAL"):
            remediation = f"""
        <div class="remedy">
          <div class="remedy-head">REMEDIATION</div>
          <div class="remedy-body">{_esc(f.remediation)}</div>
        </div>"""
        matched = ""
        if f.marker_matches:
            chips = "".join(
                f'<code class="marker">{_esc(m)}</code>' for m in f.marker_matches
            )
            matched = f'<div class="matched"><span>leaked&nbsp;markers</span>{chips}</div>'
        cards.append(f"""
    <article class="finding" style="--vc:{vc};animation-delay:{0.04 * i:.2f}s">
      <header class="f-head">
        <div class="f-id-wrap">
          <code class="f-id">{_esc(f.id)}</code>
          <div class="f-name">{_esc(f.name)}{_badges(f)}</div>
          <div class="f-cat">{_esc(f.category)} · {_esc(f.owasp)}</div>
        </div>
        <div class="f-pills">
          <span class="pill" style="--p:{vc}">{_esc(v)}</span>
          <span class="pill pill-ghost" style="--p:{sc}">{_esc(f.severity.value)}</span>
        </div>
      </header>
      <div class="f-reason">{_esc(f.reason)}</div>
      {matched}
      <div class="f-technique"><span>technique</span> {_esc(f.technique)}</div>
      <details class="f-convo">
        <summary>View conversation transcript</summary>
        <div class="convo">{_transcript(f)}</div>
      </details>
      {remediation}
    </article>""")
    return "".join(cards)


_CSS = """
:root{
  --bg:#0a0712; --bg2:#0f0b1c;
  --surface:#161122; --surface2:#1d1730;
  --line:rgba(255,255,255,.07); --line2:rgba(255,255,255,.12);
  --ink:#f4f1fb; --muted:#a39fb8; --faint:#6f6a85;
  --brand:#ff2e88; --brand2:#a855f7;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; padding:48px 20px 80px;
  font-family:"IBM Plex Sans",-apple-system,Segoe UI,Roboto,sans-serif;
  color:var(--ink); line-height:1.5;
  background:
    radial-gradient(900px 520px at 12% -8%, rgba(255,46,136,.18), transparent 60%),
    radial-gradient(820px 480px at 96% 4%, rgba(168,85,247,.16), transparent 58%),
    linear-gradient(180deg,var(--bg2),var(--bg));
  background-attachment:fixed;
  min-height:100vh;
}
.shell{max-width:1120px;margin:0 auto}
a{color:var(--brand)}

/* ---- masthead ---- */
.masthead{display:flex;justify-content:space-between;align-items:flex-end;
  gap:24px;flex-wrap:wrap;margin-bottom:36px;
  animation:rise .6s cubic-bezier(.2,.7,.2,1) both}
.brand{display:flex;align-items:center;gap:14px}
.mark{width:46px;height:46px;flex:none;border-radius:13px;
  background:linear-gradient(135deg,var(--brand),var(--brand2));
  display:grid;place-items:center;
  box-shadow:0 8px 30px rgba(255,46,136,.45);position:relative}
.mark svg{width:26px;height:26px}
.wordmark{font-family:"Sora",sans-serif;font-weight:700;font-size:26px;letter-spacing:-.02em;line-height:1}
.wordmark b{background:linear-gradient(120deg,#fff 30%,var(--brand) 120%);
  -webkit-background-clip:text;background-clip:text;color:transparent}
.tagline{color:var(--muted);font-size:12.5px;margin-top:3px;letter-spacing:.01em}
.meta{text-align:right;font-size:12px;color:var(--muted);font-family:"IBM Plex Mono",monospace}
.meta .scan{color:var(--ink);font-size:13px}
.meta .pin{display:inline-block;margin-top:6px;padding:3px 10px;border:1px solid var(--line2);
  border-radius:999px;color:var(--faint);letter-spacing:.08em;text-transform:uppercase;font-size:10px}

/* ---- hero bento ---- */
.hero{display:grid;grid-template-columns:300px 1fr;gap:18px;margin-bottom:18px}
.card{background:linear-gradient(180deg,var(--surface2),var(--surface));
  border:1px solid var(--line);border-radius:20px;
  box-shadow:0 1px 0 rgba(255,255,255,.04) inset, 0 24px 60px -30px rgba(0,0,0,.8);
  animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
.card-pad{padding:26px}
.section-tag{font-family:"IBM Plex Mono",monospace;font-size:11px;letter-spacing:.18em;
  text-transform:uppercase;color:var(--faint);margin:0 0 16px}

.grade-card{display:grid;place-items:center;text-align:center}
.ring-wrap{position:relative;width:200px;height:200px}
.ring{width:200px;height:200px;display:block}
.ring-track{fill:none;stroke:rgba(255,255,255,.07);stroke-width:14}
.ring-fill{fill:none;stroke-width:14;stroke-linecap:round;
  filter:drop-shadow(0 0 10px currentColor);
  animation:sweep 1.1s cubic-bezier(.3,.8,.2,1) .25s both}
.ring-center{position:absolute;inset:0;display:grid;place-content:center;gap:2px}
.ring-grade{font-family:"Sora",sans-serif;font-weight:800;font-size:62px;line-height:.9}
.ring-score{font-family:"IBM Plex Mono",monospace;font-size:18px;color:var(--ink)}
.ring-score span{color:var(--faint);font-size:12px}
.ring-label{font-size:10px;letter-spacing:.22em;color:var(--faint);margin-top:4px}

.kpi-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.kpi{position:relative;padding:22px 22px 20px;border-radius:18px;
  background:linear-gradient(180deg,var(--surface2),var(--surface));
  border:1px solid var(--line);overflow:hidden}
.kpi::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--c)}
.kpi::before{content:"";position:absolute;right:-40px;top:-40px;width:120px;height:120px;border-radius:50%;
  background:radial-gradient(circle,var(--c),transparent 70%);opacity:.16}
.kpi-dot{width:9px;height:9px;border-radius:50%;background:var(--c);
  box-shadow:0 0 12px var(--c);margin-bottom:14px}
.kpi-val{font-family:"Sora",sans-serif;font-weight:700;font-size:46px;line-height:.95;color:var(--c)}
.kpi-label{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-top:6px}
.kpi-hint{font-size:11.5px;color:var(--faint);margin-top:3px}

/* ---- owasp bars ---- */
.full{margin-top:18px}
.bars{display:flex;flex-direction:column;gap:11px}
.bar-row{display:grid;grid-template-columns:230px 1fr 64px;align-items:center;gap:16px}
.bar-label{font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-track{height:14px;border-radius:8px;background:rgba(46,230,166,.18);position:relative;
  min-width:8px;overflow:hidden;animation:grow .9s cubic-bezier(.2,.8,.2,1) both}
.bar-row.clean .bar-track{box-shadow:inset 0 0 0 1px rgba(46,230,166,.3)}
.bar-vuln{position:absolute;left:0;top:0;bottom:0;border-radius:8px 0 0 8px;
  background:linear-gradient(90deg,#ff2e88,#ff4d6d);box-shadow:0 0 14px rgba(255,77,109,.6)}
.bar-count{font-family:"IBM Plex Mono",monospace;font-size:12.5px;text-align:right}
.c-vuln{color:var(--brand);font-weight:600}
.c-sep{color:var(--faint);margin:0 1px}
.c-total{color:var(--muted)}
.bar-row.clean .c-vuln{color:#2ee6a6}
.empty{color:var(--faint);font-size:13px;padding:8px 0}

/* ---- findings ---- */
.findings-head{display:flex;align-items:baseline;justify-content:space-between;
  margin:42px 2px 18px;gap:16px;flex-wrap:wrap}
.findings-head h2{font-family:"Sora",sans-serif;font-size:22px;font-weight:700;margin:0;letter-spacing:-.01em}
.findings-head .sub{color:var(--faint);font-size:12.5px;font-family:"IBM Plex Mono",monospace}
.findings{display:flex;flex-direction:column;gap:14px}
.finding{position:relative;padding:22px 24px 22px 28px;border-radius:18px;
  background:linear-gradient(180deg,var(--surface2),var(--surface));
  border:1px solid var(--line);overflow:hidden;
  animation:rise .5s cubic-bezier(.2,.7,.2,1) both}
.finding::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;
  background:var(--vc);box-shadow:0 0 22px var(--vc)}
.f-head{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;flex-wrap:wrap}
.f-id{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--brand);
  background:rgba(255,46,136,.1);border:1px solid rgba(255,46,136,.25);
  padding:2px 8px;border-radius:6px}
.f-name{font-family:"Sora",sans-serif;font-weight:600;font-size:17px;margin-top:9px;
  display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.f-cat{color:var(--faint);font-size:12px;margin-top:3px;font-family:"IBM Plex Mono",monospace}
.f-pills{display:flex;gap:8px;flex:none}
.pill{font-family:"IBM Plex Mono",monospace;font-size:11px;font-weight:600;letter-spacing:.04em;
  padding:5px 11px;border-radius:999px;color:#0a0712;background:var(--p);white-space:nowrap}
.pill-ghost{background:transparent;color:var(--p);border:1px solid var(--p);text-transform:uppercase}
.badge{font-family:"IBM Plex Mono",monospace;font-size:9.5px;font-weight:600;letter-spacing:.06em;
  padding:2px 7px;border-radius:5px;color:#fff}
.badge-lang{background:rgba(168,85,247,.85)}
.badge-mt{background:rgba(77,208,255,.85);color:#04222e}
.f-reason{margin-top:14px;font-size:14px;color:#e7e3f2}
.matched{margin-top:12px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.matched>span{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
.marker{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:#ff9bb3;
  background:rgba(255,77,109,.12);border:1px solid rgba(255,77,109,.3);padding:2px 8px;border-radius:6px}
.f-technique{margin-top:13px;font-size:13px;color:var(--muted);font-style:italic}
.f-technique span{font-style:normal;font-family:"IBM Plex Mono",monospace;font-size:10px;
  letter-spacing:.1em;text-transform:uppercase;color:var(--faint);margin-right:8px}
.f-convo{margin-top:14px}
.f-convo summary{cursor:pointer;list-style:none;font-size:12.5px;color:var(--brand);
  font-family:"IBM Plex Mono",monospace;display:inline-flex;align-items:center;gap:6px;
  padding:6px 0;user-select:none}
.f-convo summary::-webkit-details-marker{display:none}
.f-convo summary::before{content:"▸";transition:transform .2s}
.f-convo[open] summary::before{transform:rotate(90deg)}
.convo{margin-top:10px;border-left:1px solid var(--line2);padding-left:16px;
  display:flex;flex-direction:column;gap:14px}
.turn-head{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.14em;
  color:var(--brand);margin-bottom:5px}
.turn-head.bot{color:#4dd0ff;margin-top:11px}
.turn-no{opacity:.6;margin-right:6px}
.msg{font-family:"IBM Plex Mono",monospace;font-size:12px;white-space:pre-wrap;word-break:break-word;
  padding:11px 13px;border-radius:10px;border:1px solid var(--line)}
.msg-atk{background:rgba(255,46,136,.07)}
.msg-bot{background:rgba(255,255,255,.03)}
.remedy{margin-top:16px;border:1px solid rgba(46,230,166,.28);background:rgba(46,230,166,.07);
  border-radius:12px;padding:13px 15px}
.remedy-head{font-family:"IBM Plex Mono",monospace;font-size:10px;letter-spacing:.16em;
  color:#2ee6a6;margin-bottom:5px}
.remedy-head::before{content:"✓ "}
.remedy-body{font-size:13px;color:#cdeede}

/* ---- footer ---- */
.foot{margin-top:48px;padding-top:22px;border-top:1px solid var(--line);
  color:var(--faint);font-size:11.5px;line-height:1.7;display:flex;
  justify-content:space-between;gap:18px;flex-wrap:wrap}
.foot b{color:var(--muted)}
.foot .by{font-family:"IBM Plex Mono",monospace}

/* ---- motion ---- */
@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes sweep{from{stroke-dasharray:0 9999}}
@keyframes grow{from{transform:scaleX(0);transform-origin:left}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
@media (max-width:780px){
  .hero{grid-template-columns:1fr}
  .bar-row{grid-template-columns:120px 1fr 56px;gap:10px}
  body{padding:28px 14px 60px}
}
"""

_LOGO = (
    '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    '<path d="M12 2 4 5v6c0 5 3.4 8.3 8 11 4.6-2.7 8-6 8-11V5l-8-3Z" '
    'fill="#fff" fill-opacity=".95"/>'
    '<path d="m13.2 7-4 6.2h2.6L10.6 18l5-7h-3l1.6-4Z" fill="#ff2e88"/>'
    "</svg>"
)


def html_report(summary: dict, findings: list[Finding], scan_id: str) -> str:
    score = summary["score"]
    grade = summary["grade"]
    total = summary["total"]
    categories = len(summary["byCategory"])
    owasp_n = len(summary["byOwasp"])

    kpis = (
        _kpi("Vulnerable", summary["vulnerable"], "#ff4d6d", "defenses breached")
        + _kpi("Partial", summary["partial"], "#ffb020", "partial leakage")
        + _kpi("Safe", summary["safe"], "#2ee6a6", "held the line")
        + _kpi("Attacks", total, "#a855f7", f"{categories} categories")
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BrechaBot — Red-Team Report · {_esc(scan_id)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{_CSS}</style>
</head>
<body>
<div class="shell">

  <header class="masthead">
    <div class="brand">
      <div class="mark">{_LOGO}</div>
      <div>
        <div class="wordmark">Brecha<b>Bot</b></div>
        <div class="tagline">AI chatbot red-team scanner · OWASP LLM Top 10</div>
      </div>
    </div>
    <div class="meta">
      <div class="scan">{_esc(scan_id)}</div>
      <div>{total} attacks · {categories} categories · {owasp_n} OWASP classes</div>
      <div class="pin">Confidential · authorized testing</div>
    </div>
  </header>

  <section class="hero">
    <div class="card card-pad grade-card" style="animation-delay:.05s">
      {_score_ring(score, grade)}
    </div>
    <div class="kpi-grid">
      {kpis}
    </div>
  </section>

  <section class="card card-pad full" style="animation-delay:.12s">
    <p class="section-tag">OWASP LLM Top 10 Exposure</p>
    <div class="bars">
      {_owasp_bars(summary["byOwasp"])}
    </div>
  </section>

  <div class="findings-head">
    <h2>Detailed Findings</h2>
    <div class="sub">sorted by severity · {total} total</div>
  </div>
  <section class="findings">
    {_finding_cards(findings)}
  </section>

  <footer class="foot">
    <div>
      <b>Two-layer verdict engine</b> — deterministic leak-marker regex + LLM judge.
      Findings mapped to the OWASP LLM Top 10 (2025) with remediation guidance.
    </div>
    <div class="by">Generated by BrechaBot</div>
  </footer>

</div>
</body>
</html>"""
