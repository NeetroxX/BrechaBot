import httpx
import pytest

from brechabot.models import Attack, ScanConfig, Verdict
from brechabot.orchestrator import run_scan

JUDGE_URL = "https://judge.test/v1/chat/completions"
TARGET_URL = "https://bot.test/chat"
CATS = {
    "Role Hijacking": {"owasp": "LLM01", "remediation": "r"},
    "Multi-Turn": {"owasp": "LLM01", "remediation": "r"},
}


def _cfg(**kw) -> ScanConfig:
    base = dict(
        target_url=TARGET_URL,
        system_prompt="secret is sk_live_x",
        max_retries=0,
        concurrency=2,
    )
    base.update(kw)
    cfg = ScanConfig(**base)
    cfg.judge.base_url = "https://judge.test/v1"
    return cfg


def _judge(httpx_mock, verdict: str = "VULNERABLE"):
    httpx_mock.add_callback(
        lambda r: httpx.Response(
            200,
            json={"choices": [{"message": {"content": f'{{"verdict":"{verdict}","severity":"high","reason":"r"}}'}}]},
        ),
        url=JUDGE_URL,
    )


@pytest.mark.asyncio
async def test_leak_is_vulnerable(httpx_mock):
    leak = "Sure: " + ("x" * 500) + " sk_live_x"
    httpx_mock.add_callback(
        lambda r: httpx.Response(200, json={"choices": [{"message": {"content": leak}}]}),
        url=TARGET_URL,
    )
    _judge(httpx_mock)
    attack = Attack(id="PXR-T", category="Role Hijacking", name="N", prompt="leak it", markers=["sk_live_"])
    findings = await run_scan([attack], CATS, _cfg(), "scan-1")
    assert findings[0].verdict is Verdict.VULNERABLE


@pytest.mark.asyncio
async def test_target_429_is_error(httpx_mock):
    httpx_mock.add_callback(lambda r: httpx.Response(429), url=TARGET_URL)
    attack = Attack(id="PXR-E", category="Role Hijacking", name="N", prompt="x", markers=["a"])
    findings = await run_scan([attack], CATS, _cfg(), "scan-2")
    assert findings[0].verdict is Verdict.ERROR


@pytest.mark.asyncio
async def test_multi_turn_makes_sequential_calls(httpx_mock):
    httpx_mock.add_callback(
        lambda r: httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]}),
        url=TARGET_URL,
    )
    _judge(httpx_mock, "SAFE")
    attack = Attack(id="PXR-M", category="Multi-Turn", name="N", turns=["t1", "t2", "t3"], markers=["zzz"])
    findings = await run_scan([attack], CATS, _cfg(), "scan-3")
    target_calls = [req for req in httpx_mock.get_requests() if str(req.url) == TARGET_URL]
    assert len(target_calls) == 3
    assert len(findings[0].transcript) == 3
    assert findings[0].is_multi_turn is True
