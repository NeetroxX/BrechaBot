from __future__ import annotations

from typing import Any

from .base import Message, fallback_extract, non_system, system_of


class AnthropicAdapter:
    def build_request(self, messages: list[Message], cfg: Any) -> dict[str, Any]:
        return {
            "model": cfg.target_model,
            "max_tokens": 1024,
            "system": system_of(messages),
            "messages": non_system(messages),
        }

    def parse_reply(self, resp: Any) -> str:
        if isinstance(resp, dict):
            content = resp.get("content")
            if isinstance(content, list):
                return "".join(c.get("text", "") for c in content if isinstance(c, dict))
            if isinstance(resp.get("completion"), str):
                return resp["completion"]
        return fallback_extract(resp)
