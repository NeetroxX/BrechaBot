import pytest

from brechabot.judge.llm_judge import judge


class FakeClient:
    def __init__(self, reply: str):
        self._reply = reply

    async def complete(self, system: str, user: str) -> str:
        return self._reply


@pytest.mark.asyncio
async def test_parses_clean_json():
    client = FakeClient('{"verdict": "vulnerable", "severity": "High", "reason": "leaked"}')
    out = await judge(client, "sys", "atk", "reply")
    assert out == {"verdict": "VULNERABLE", "severity": "high", "reason": "leaked"}


@pytest.mark.asyncio
async def test_extracts_json_embedded_in_prose():
    client = FakeClient('Sure: {"verdict":"SAFE","severity":"none","reason":"ok"} done')
    out = await judge(client, "sys", "atk", "reply")
    assert out["verdict"] == "SAFE"


@pytest.mark.asyncio
async def test_unparseable_becomes_unknown():
    client = FakeClient("no json here")
    out = await judge(client, "sys", "atk", "reply")
    assert out["verdict"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_client_error_becomes_unknown():
    class Boom:
        async def complete(self, system: str, user: str) -> str:
            raise RuntimeError("down")

    out = await judge(Boom(), "sys", "atk", "reply")
    assert out["verdict"] == "UNKNOWN"
