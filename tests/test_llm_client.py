import pytest

from brechabot.llm.client import LLMClient
from brechabot.models import JudgeConfig


@pytest.mark.asyncio
async def test_complete_posts_and_returns_content(httpx_mock):
    httpx_mock.add_response(
        url="https://judge.test/v1/chat/completions",
        json={"choices": [{"message": {"content": "VERDICT"}}]},
    )
    client = LLMClient(JudgeConfig(base_url="https://judge.test/v1", model="m", api_key="k"))
    out = await client.complete("sys", "user")
    assert out == "VERDICT"

    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "Bearer k"
