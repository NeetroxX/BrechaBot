from __future__ import annotations

import html as _html

from ..models import Finding

_SEV_COLOR = {"high": "#dc2626", "medium": "#ea580c", "low": "#ca8a04", "none": "#16a34a"}
_ROW_COLOR = {"VULNERABLE": "#fee2e2", "PARTIAL": "#fef3c7", "SAFE": "#dcfce7"}


def _esc(value: object) -> str:
    return _html.escape("" if value is None else str(value))


def _sev_color(severity: str) -> str:
    return _SEV_COLOR.get(severity, "#6b7280")


def _row_color(verdict: str) -> str:
    return _ROW_COLOR.get(verdict, "#f3f4f6")


def _grade_color(score: int) -> str:
    if score >= 80:
        return "#16a34a"
    if score >= 60:
        return "#ea580c"
    return "#dc2626"


def _owasp_rows(by_owasp: dict[str, dict[str, int]]) -> str:
    rows = sorted(by_owasp.items(), key=lambda kv: -kv[1]["vulnerable"])
    cells = []
    for key, val in rows:
        color = "#dc2626" if val["vulnerable"] else "#16a34a"
        cells.append(
            f'<tr><td style="padding:8px;border:1px solid #e5e7eb">{_esc(key)}</td>'
            f'<td style="padding:8px;border:1px solid #e5e7eb;text-align:center">{val["total"]}</td>'
            f'<td style="padding:8px;border:1px solid #e5e7eb;text-align:center;color:{color};'
            f'font-weight:600">{val["vulnerable"]}</td></tr>'
        )
    return "".join(cells)


def _finding_rows(findings: list[Finding]) -> str:
    weight = {"high": 3, "medium": 2, "low": 1, "none": 0}
    ordered = sorted(findings, key=lambda f: -weight.get(f.severity.value, 0))
    out = []
    for f in ordered:
        lang_badge = (
            f'<span style="background:#4338ca;color:white;font-size:10px;padding:1px 6px;'
            f'border-radius:4px;margin-left:6px">{_esc(f.lang.upper())}</span>'
            if f.lang and f.lang != "en"
            else ""
        )
        mt_badge = (
            '<span style="background:#7c3aed;color:white;font-size:10px;padding:1px 6px;'
            'border-radius:4px;margin-left:6px">MULTI-TURN</span>'
            if f.is_multi_turn
            else ""
        )
        convo = []
        for turn in f.transcript:
            convo.append(
                f'<div style="color:#6b7280;font-size:10px">TURN {turn.turn} — ATTACKER</div>'
                f'<div style="font-family:monospace;font-size:11px;background:#f3f4f6;padding:6px;'
                f'border-radius:4px;white-space:pre-wrap">{_esc(turn.user[:600])}</div>'
                f'<div style="color:#6b7280;font-size:10px;margin-top:4px">TURN {turn.turn} — BOT</div>'
                f'<div style="font-family:monospace;font-size:11px;background:#fff;padding:6px;'
                f'border-radius:4px;border:1px solid #e5e7eb;white-space:pre-wrap">'
                f"{_esc(turn.bot[:600])}</div>"
            )
        convo_html = "".join(convo)
        remediation = ""
        if f.verdict.value in ("VULNERABLE", "PARTIAL"):
            remediation = (
                '<div style="margin-top:8px;padding:8px;background:#eff6ff;border-left:3px solid '
                '#2563eb;border-radius:4px"><div style="color:#1e40af;font-size:10px;font-weight:600">'
                f'✓ REMEDIATION</div><div style="font-size:12px;color:#1e3a8a">{_esc(f.remediation)}'
                "</div></div>"
            )
        matched = ""
        if f.marker_matches:
            matched = (
                '<div style="margin-top:6px;font-family:monospace;font-size:10px;color:#7f1d1d">'
                f'matched: {_esc(", ".join(f.marker_matches))}</div>'
            )
        out.append(
            f'<tr style="background:{_row_color(f.verdict.value)};border-top:2px solid #d1d5db">'
            f'<td style="padding:10px;border:1px solid #e5e7eb;font-family:monospace;font-size:11px;'
            f'vertical-align:top">{_esc(f.id)}</td>'
            f'<td style="padding:10px;border:1px solid #e5e7eb;vertical-align:top"><b>{_esc(f.name)}</b>'
            f'{lang_badge}{mt_badge}<div style="font-size:11px;color:#6b7280;margin-top:4px">'
            f"{_esc(f.category)}</div></td>"
            f'<td style="padding:10px;border:1px solid #e5e7eb;font-size:11px;vertical-align:top">'
            f"{_esc(f.owasp)}</td>"
            f'<td style="padding:10px;border:1px solid #e5e7eb;font-weight:700;vertical-align:top">'
            f"{_esc(f.verdict.value)}</td>"
            f'<td style="padding:10px;border:1px solid #e5e7eb;color:{_sev_color(f.severity.value)};'
            f'font-weight:600;vertical-align:top">{_esc(f.severity.value)}</td>'
            f'<td style="padding:10px;border:1px solid #e5e7eb;font-size:12px;vertical-align:top">'
            f"{_esc(f.reason)}{matched}</td></tr>"
            f'<tr style="background:#f9fafb"><td colspan="6" style="padding:10px;border:1px solid '
            f'#e5e7eb;font-size:12px;color:#374151"><div style="color:#6b7280;font-size:10px;'
            f'margin-bottom:4px">TECHNIQUE</div><i>{_esc(f.technique)}</i>'
            f'<div style="margin-top:8px">{convo_html}</div>{remediation}</td></tr>'
        )
    return "".join(out)


def html_report(summary: dict, findings: list[Finding], scan_id: str) -> str:
    score = summary["score"]
    grade = summary["grade"]
    categories = len(summary["byCategory"])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>AI Chatbot Red Team Report</title></head>
<body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:1150px;margin:24px auto;color:#111827;background:#fafafa;padding:24px">
<div style="background:white;padding:32px;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1)">
<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #dc2626;padding-bottom:16px;margin-bottom:24px">
<div><h1 style="margin:0;font-size:28px">AI Chatbot Red Team Report</h1>
<div style="color:#6b7280;font-size:13px;margin-top:4px">{summary["total"]} attacks · {categories} categories · OWASP LLM Top 10 mapped · Scan {_esc(scan_id)}</div></div>
<div style="text-align:center;padding:16px 24px;background:{_grade_color(score)};color:white;border-radius:8px">
<div style="font-size:48px;font-weight:700;line-height:1">{grade}</div>
<div style="font-size:14px;font-weight:600">{score}/100</div></div></div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px">
<div style="padding:16px;background:#fee2e2;border-radius:8px"><div style="font-size:11px;color:#7f1d1d;font-weight:600">VULNERABLE</div><div style="font-size:28px;font-weight:700;color:#dc2626">{summary["vulnerable"]}</div></div>
<div style="padding:16px;background:#fef3c7;border-radius:8px"><div style="font-size:11px;color:#78350f;font-weight:600">PARTIAL</div><div style="font-size:28px;font-weight:700;color:#ea580c">{summary["partial"]}</div></div>
<div style="padding:16px;background:#dcfce7;border-radius:8px"><div style="font-size:11px;color:#14532d;font-weight:600">SAFE</div><div style="font-size:28px;font-weight:700;color:#16a34a">{summary["safe"]}</div></div>
<div style="padding:16px;background:#e0e7ff;border-radius:8px"><div style="font-size:11px;color:#3730a3;font-weight:600">TOTAL ATTACKS</div><div style="font-size:28px;font-weight:700;color:#4338ca">{summary["total"]}</div></div></div>
<h2 style="font-size:18px;margin-top:32px">OWASP LLM Top 10 Exposure</h2>
<table style="width:100%;border-collapse:collapse;margin-bottom:24px;font-size:14px"><thead><tr style="background:#7f1d1d;color:white"><th style="padding:10px;text-align:left">OWASP Category</th><th style="padding:10px">Tested</th><th style="padding:10px">Vulnerable</th></tr></thead><tbody>{_owasp_rows(summary["byOwasp"])}</tbody></table>
<h2 style="font-size:18px;margin-top:32px">Detailed Findings (sorted by severity)</h2>
<table style="width:100%;border-collapse:collapse;font-size:14px"><thead><tr style="background:#1f2937;color:white"><th style="padding:10px;text-align:left">ID</th><th style="padding:10px;text-align:left">Attack</th><th style="padding:10px;text-align:left">OWASP</th><th style="padding:10px;text-align:left">Verdict</th><th style="padding:10px;text-align:left">Severity</th><th style="padding:10px;text-align:left">Analysis</th></tr></thead><tbody>{_finding_rows(findings)}</tbody></table>
<div style="margin-top:32px;padding-top:16px;border-top:1px solid #e5e7eb;color:#6b7280;font-size:11px">Two-layer verdict engine: deterministic leak-marker regex + LLM judge. Findings mapped to OWASP LLM Top 10 (2025) with remediation guidance. Generated by the Prompt Exploitation Registry (PXR).</div>
</div></body></html>"""
