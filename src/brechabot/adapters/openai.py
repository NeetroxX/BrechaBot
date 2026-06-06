from __future__ import annotations

from typing import Any

from .base import Message, fallback_extract


class OpenAIAdapter:
    def build_request(self, messages: list[Message], cfg: Any) -> dict[str, Any]:
        return {"model": cfg.target_model, "messages": messages}

    def parse_reply(self, resp: Any) -> str:
        try:
            if isinstance(resp, dict) and resp.get("choices"):
                choice = resp["choices"][0]
                message = choice.get("message") or {}
                return message.get("content") or choice.get("text") or ""
        except (KeyError, IndexError, TypeError):
            pass
        return fallback_extract(resp)
