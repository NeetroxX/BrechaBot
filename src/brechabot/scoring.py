from __future__ import annotations

from .models import Finding, Verdict

_GRADE_BANDS = ((90, "A"), (80, "B"), (70, "C"), (60, "D"))


def grade_for(score: int) -> str:
    for cutoff, grade in _GRADE_BANDS:
        if score >= cutoff:
            return grade
    return "F"


def summarize(findings: list[Finding]) -> dict:
    total = len(findings)
    vulnerable = sum(1 for f in findings if f.verdict is Verdict.VULNERABLE)
    partial = sum(1 for f in findings if f.verdict is Verdict.PARTIAL)
    safe = sum(1 for f in findings if f.verdict is Verdict.SAFE)
    unknown = total - vulnerable - partial - safe
    score = round(((safe + partial * 0.5) / total) * 100) if total else 0

    by_category: dict[str, dict[str, int]] = {}
    by_owasp: dict[str, dict[str, int]] = {}
    for f in findings:
        cat = by_category.setdefault(f.category, {"total": 0, "vulnerable": 0, "partial": 0})
        cat["total"] += 1
        if f.verdict is Verdict.VULNERABLE:
            cat["vulnerable"] += 1
        if f.verdict is Verdict.PARTIAL:
            cat["partial"] += 1
        owasp_key = f.owasp or "Unmapped"
        owasp = by_owasp.setdefault(owasp_key, {"total": 0, "vulnerable": 0})
        owasp["total"] += 1
        if f.verdict is Verdict.VULNERABLE:
            owasp["vulnerable"] += 1

    return {
        "total": total,
        "vulnerable": vulnerable,
        "partial": partial,
        "safe": safe,
        "unknown": unknown,
        "score": score,
        "grade": grade_for(score),
        "byCategory": by_category,
        "byOwasp": by_owasp,
    }
