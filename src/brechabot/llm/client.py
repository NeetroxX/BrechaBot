from __future__ import annotations

import httpx

from ..models import JudgeConfig


class LLMClient:
    """Minimal async client for any OpenAI-compatible /chat/completions endpoint."""

    def __init__(self, cfg: JudgeConfig, timeout_s: float = 60.0) -> None:
        self._cfg = cfg
        self._timeout = timeout_s

    async def complete(self, system: str, user: str) -> str:
        headers = {"Content-Type": "application/json"}
        if self._cfg.api_key:
            headers["Authorization"] = f"Bearer {self._cfg.api_key}"
        body = {
            "model": self._cfg.model,
            "temperature": self._cfg.temperature,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        url = self._cfg.base_url.rstrip("/") + "/chat/completions"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]
