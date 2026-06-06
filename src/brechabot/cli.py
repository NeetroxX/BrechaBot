from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime
from pathlib import Path

import typer
import yaml

from . import __version__
from .corpus.loader import load_corpus
from .models import JudgeConfig, ScanConfig, ScanResult
from .orchestrator import run_scan
from .report.html import html_report
from .scoring import summarize

app = typer.Typer(
    help="AI chatbot red-team engine (PXR corpus + two-layer judge).", no_args_is_help=True
)
corpus_app = typer.Typer(help="Inspect the attack corpus.")
app.add_typer(corpus_app, name="corpus")


def _now() -> str:
    return datetime.now(UTC).isoformat()


@app.command()
def version() -> None:
    """Print the engine and corpus versions."""
    typer.echo(f"brechabot {__version__} ({load_corpus().version})")


@corpus_app.command("list")
def corpus_list(pack: list[str] | None = typer.Option(None, "--pack")) -> None:
    """List attacks and OWASP coverage."""
    corpus = load_corpus(pack or None)
    for attack in corpus.attacks:
        kind = "multi" if attack.is_multi_turn else "single"
        typer.echo(
            f"{attack.id}  [{attack.severity.value:<6}] {kind:<6} {attack.category} — {attack.name}"
        )
    typer.echo(f"\nPacks: {', '.join(corpus.packs)} — {len(corpus.attacks)} attacks")


@corpus_app.command("validate")
def corpus_validate(pack: list[str] | None = typer.Option(None, "--pack")) -> None:
    """Validate the corpus loads and every attack resolves OWASP + remediation."""
    corpus = load_corpus(pack or None)
    missing = [a.id for a in corpus.attacks if a.category not in corpus.categories]
    if missing:
        typer.echo(f"INVALID: attacks with unmapped category: {missing}")
        raise typer.Exit(code=1)
    typer.echo(f"OK: {len(corpus.attacks)} attacks, {len(corpus.categories)} categories, all mapped.")


@app.command()
def scan(
    target_url: str = typer.Option(..., "--target-url", help="Target chatbot endpoint."),
    schema: str = typer.Option("openai", "--schema", help="openai|anthropic|cohere|rest"),
    target_model: str = typer.Option("gpt-4o-mini", "--target-model"),
    auth: str | None = typer.Option(None, "--auth", help='e.g. "Authorization: Bearer X"'),
    system_prompt_file: Path | None = typer.Option(None, "--system-prompt-file"),
    judge_base_url: str = typer.Option("http://localhost:11434/v1", "--judge-base-url"),
    judge_model: str = typer.Option("gemma4:31b-cloud", "--judge-model"),
    judge_key: str | None = typer.Option(None, "--judge-key"),
    profile: str = typer.Option("full", "--profile"),
    concurrency: int = typer.Option(4, "--concurrency"),
    pack: list[str] | None = typer.Option(None, "--pack", help="Attack pack(s): builtin name or path (repeatable)."),
    out: Path = typer.Option(Path("report.json"), "--out"),
    html: Path | None = typer.Option(None, "--html"),
    config: Path | None = typer.Option(None, "--config", help="YAML config (overrides flags)."),
) -> None:
    """Run a red-team scan against a target chatbot."""
    if config is not None:
        cfg = ScanConfig.model_validate(yaml.safe_load(config.read_text(encoding="utf-8")))
    else:
        system_prompt = (
            system_prompt_file.read_text(encoding="utf-8")
            if system_prompt_file
            else "You are a helpful assistant."
        )
        cfg = ScanConfig(
            target_url=target_url,
            schema=schema,  # type: ignore[arg-type]
            target_model=target_model,
            system_prompt=system_prompt,
            auth_header=auth,
            judge=JudgeConfig(base_url=judge_base_url, model=judge_model, api_key=judge_key),
            profile=profile,
            concurrency=concurrency,
        )

    corpus = load_corpus(pack or None)
    scan_id = str(int(time.time() * 1000))
    started = _now()
    findings = asyncio.run(run_scan(corpus.attacks, corpus.categories, cfg, scan_id))
    finished = _now()

    summary = summarize(findings)
    report_html = html_report(summary, findings, scan_id)
    result = ScanResult(
        scan_id=scan_id,
        corpus_version=corpus.version,
        started_at=started,
        finished_at=finished,
        summary=summary,
        findings=findings,
        html=report_html,
    )
    out.write_text(result.model_dump_json(by_alias=True, indent=2), encoding="utf-8")
    if html is not None:
        html.write_text(report_html, encoding="utf-8")

    typer.echo(
        f"Grade {summary['grade']}  Score {summary['score']}/100  "
        f"VULN:{summary['vulnerable']} PARTIAL:{summary['partial']} "
        f"SAFE:{summary['safe']} /{summary['total']}  -> {out}"
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
