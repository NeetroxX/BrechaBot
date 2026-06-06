from brechabot.models import Finding, Severity, TranscriptTurn, Verdict
from brechabot.report.html import html_report
from brechabot.scoring import summarize


def _vuln_finding() -> Finding:
    return Finding(
        id="PXR-030", name="DELIMITER SHADOW", category="Token Smuggling", technique="t",
        owasp="LLM07: System Prompt Leakage", remediation="Do not disclose.", lang="en",
        is_multi_turn=False, transcript=[TranscriptTurn(turn=1, user="atk", bot="leaked sk_live_x")],
        attack_prompt="atk", bot_reply="leaked sk_live_x", verdict=Verdict.VULNERABLE,
        severity=Severity.HIGH, reason="Leak markers matched", marker_matches=["sk_live_"],
    )


def test_report_contains_key_sections():
    findings = [_vuln_finding()]
    html = html_report(summarize(findings), findings, "scan-123")
    assert "<!doctype html>" in html.lower()
    assert "OWASP LLM Top 10 Exposure" in html
    assert "PXR-030" in html
    assert "DELIMITER SHADOW" in html
    assert "scan-123" in html
    assert "REMEDIATION" in html  # vulnerable findings show remediation


def test_report_escapes_html_in_replies():
    f = _vuln_finding()
    f.bot_reply = "<script>alert(1)</script>"
    f.transcript = [TranscriptTurn(turn=1, user="u", bot="<script>alert(1)</script>")]
    html = html_report(summarize([f]), [f], "s")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
