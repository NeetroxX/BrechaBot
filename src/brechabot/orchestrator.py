from __future__ import annotations

import asyncio

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .adapters import get_adapter
from .adapters.base import Message, TargetAdapter
from .corpus.loader import owasp_for, remediation_for
from .judge.combine import combine
from .judge.llm_judge import judge as run_judge
from .llm.client import LLMClient
from .models import (
    Attack,
    Finding,
    ScanConfig,
    TranscriptTurn,
    Verdict,
    to_severity,
    to_verdict,
)

_TURN_SEP = "\n--- next turn ---\n"


class _RetryableStatus(Exception):
    """Raised for transient target HTTP statuses so tenacity retries them."""


def _parse_auth_header(auth_header: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if not auth_header:
        return headers
    if ":" in auth_header:
        key, value = auth_header.split(":", 1)
        headers[key.strip()] = value.strip()
    else:
        headers["Authorization"] = auth_header
    return headers


async def _call_target(
    http: httpx.AsyncClient,
    url: str,
    body: dict,
    headers: dict[str, str],
    timeout: float,
    max_retries: int,
) -> tuple[object | None, str | None]:
    @retry(
        reraise=True,
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.TransportError, _RetryableStatus)
        ),
    )
    async def _do() -> httpx.Response:
        resp = await http.post(url, json=body, headers=headers, timeout=timeout)
        if resp.status_code in (429, 500, 502, 503, 504):
            raise _RetryableStatus(f"HTTP {resp.status_code}")
        return resp

    try:
        resp = await _do()
    except Exception as exc:  # noqa: BLE001 - any failure becomes an ERROR finding
        return None, str(exc)
    if resp.status_code >= 400:
        return None, f"HTTP {resp.status_code}"
    try:
        return resp.json(), None
    except Exception:  # noqa: BLE001 - non-JSON body, fall back to text
        return resp.text, None


async def _run_attack(
    attack: Attack,
    cfg: ScanConfig,
    adapter: TargetAdapter,
    llm: LLMClient,
    categories: dict[str, dict[str, str]],
    http: httpx.AsyncClient,
    sem: asyncio.Semaphore,
) -> Finding:
    async with sem:
        headers = _parse_auth_header(cfg.auth_header)
        messages: list[Message] = [{"role": "system", "content": cfg.system_prompt}]
        transcript: list[TranscriptTurn] = []
        reply = ""
        error: str | None = None
        turns = attack.turn_list

        for index, turn in enumerate(turns):
            messages.append({"role": "user", "content": turn})
            body = adapter.build_request(messages, cfg)
            parsed, err = await _call_target(
                http, cfg.target_url, body, headers, cfg.timeout_s, cfg.max_retries
            )
            if err is not None:
                error = err
                transcript.append(TranscriptTurn(turn=index + 1, user=turn, bot=f"[error] {err}"))
                break
            reply = adapter.parse_reply(parsed)[:4000]
            messages.append({"role": "assistant", "content": reply})
            transcript.append(TranscriptTurn(turn=index + 1, user=turn, bot=reply))

        owasp = owasp_for(attack.category, categories)
        remediation = remediation_for(attack.category, categories)
        attack_prompt = _TURN_SEP.join(turns)

        if error is not None:
            return Finding(
                id=attack.id,
                name=attack.name,
                category=attack.category,
                technique=attack.technique,
                owasp=owasp,
                remediation=remediation,
                lang=attack.lang,
                is_multi_turn=attack.is_multi_turn,
                transcript=transcript,
                attack_prompt=attack_prompt,
                bot_reply="",
                verdict=Verdict.ERROR,
                severity=attack.severity,
                reason=f"target-error: {error}",
                marker_matches=[],
                judge_verdict="ERROR",
                judge_severity="none",
            )

        judge_result = await run_judge(llm, cfg.system_prompt, attack_prompt, reply)
        combined = combine(reply, attack.markers, attack.severity.value, judge_result)
        return Finding(
            id=attack.id,
            name=attack.name,
            category=attack.category,
            technique=attack.technique,
            owasp=owasp,
            remediation=remediation,
            lang=attack.lang,
            is_multi_turn=attack.is_multi_turn,
            transcript=transcript,
            attack_prompt=attack_prompt,
            bot_reply=reply,
            verdict=to_verdict(combined.verdict),
            severity=to_severity(combined.severity),
            reason=combined.reason,
            marker_matches=combined.marker_matches,
            judge_verdict=combined.judge_verdict,
            judge_severity=combined.judge_severity,
        )


async def run_scan(
    attacks: list[Attack],
    categories: dict[str, dict[str, str]],
    cfg: ScanConfig,
    scan_id: str,
) -> list[Finding]:
    adapter = get_adapter(cfg.target_schema)
    llm = LLMClient(cfg.judge)
    sem = asyncio.Semaphore(cfg.concurrency)
    async with httpx.AsyncClient() as http:
        tasks = [
            _run_attack(attack, cfg, adapter, llm, categories, http, sem) for attack in attacks
        ]
        return list(await asyncio.gather(*tasks))
