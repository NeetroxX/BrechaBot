import json
from pathlib import Path

from typer.testing import CliRunner

from brechabot import cli
from brechabot.models import Finding, Severity, Verdict

runner = CliRunner()


def _finding() -> Finding:
    return Finding(
        id="PXR-001", name="N", category="Role Hijacking", technique="", owasp="LLM01",
        remediation="fix", lang="en", is_multi_turn=False, transcript=[], attack_prompt="p",
        bot_reply="r", verdict=Verdict.SAFE, severity=Severity.NONE, reason="",
    )


def test_version():
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_corpus_validate():
    result = runner.invoke(cli.app, ["corpus", "validate"])
    assert result.exit_code == 0
    assert "10 attacks" in result.stdout


def test_scan_writes_report(tmp_path, monkeypatch):
    async def fake_run_scan(attacks, categories, cfg, scan_id):
        return [_finding()]

    monkeypatch.setattr(cli, "run_scan", fake_run_scan)
    out = tmp_path / "report.json"
    html = tmp_path / "report.html"
    result = runner.invoke(
        cli.app,
        ["scan", "--target-url", "https://x", "--out", str(out), "--html", str(html)],
    )
    assert result.exit_code == 0, result.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["total"] == 1
    assert data["scanId"]
    assert Path(html).exists()
    assert "Red Team Report" in html.read_text(encoding="utf-8")
