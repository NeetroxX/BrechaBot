from __future__ import annotations

from typing import Any

from .base import Message, fallback_extract, non_system, system_of


class RestAdapter:
    def build_request(self, messages: list[Message], cfg: Any) -> dict[str, Any]:
        users = [m["content"] for m in messages if m["role"] == "user"]
        return {
            "system": system_of(messages),
            "input": users[-1] if users else "",
            "messages": non_system(messages),
        }

    def parse_reply(self, resp: Any) -> str:
        return fallback_extract(resp)
