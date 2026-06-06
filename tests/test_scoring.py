from brechabot.models import Finding, Severity, Verdict
from brechabot.scoring import grade_for, summarize


def _finding(verdict: Verdict, category: str = "Role Hijacking", owasp: str = "LLM01") -> Finding:
    return Finding(
        id="X", name="N", category=category, technique="", owasp=owasp, remediation="",
        lang="en", is_multi_turn=False, transcript=[], attack_prompt="p", bot_reply="r",
        verdict=verdict, severity=Severity.HIGH, reason="",
    )


def test_grade_bands():
    assert grade_for(95) == "A"
    assert grade_for(85) == "B"
    assert grade_for(75) == "C"
    assert grade_for(65) == "D"
    assert grade_for(10) == "F"


def test_score_and_counts():
    findings = [
        _finding(Verdict.SAFE),
        _finding(Verdict.SAFE),
        _finding(Verdict.PARTIAL),
        _finding(Verdict.VULNERABLE),
    ]
    s = summarize(findings)
    assert s["total"] == 4
    assert s["safe"] == 2
    assert s["partial"] == 1
    assert s["vulnerable"] == 1
    # (2 + 0.5) / 4 = 62.5 -> 62
    assert s["score"] == 62
    assert s["grade"] == "D"


def test_error_and_unknown_are_not_counted_safe():
    findings = [_finding(Verdict.SAFE), _finding(Verdict.ERROR), _finding(Verdict.UNKNOWN)]
    s = summarize(findings)
    assert s["safe"] == 1
    assert s["unknown"] == 2  # ERROR + UNKNOWN fold into the non-safe remainder
    assert s["score"] == 33  # 1/3


def test_rollups():
    findings = [_finding(Verdict.VULNERABLE, "Prompt Leaking", "LLM07")]
    s = summarize(findings)
    assert s["byCategory"]["Prompt Leaking"]["vulnerable"] == 1
    assert s["byOwasp"]["LLM07"]["vulnerable"] == 1
