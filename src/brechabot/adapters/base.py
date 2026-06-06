from __future__ import annotations

import json
from typing import Any, Protocol

Message = dict[str, str]


class TargetAdapter(Protocol):
    def build_request(self, messages: list[Message], cfg: Any) -> dict[str, Any]: ...
    def parse_reply(self, resp: Any) -> str: ...


def system_of(messages: list[Message]) -> str:
    return next((m["content"] for m in messages if m["role"] == "system"), "")


def non_system(messages: list[Message]) -> list[Message]:
    return [m for m in messages if m["role"] != "system"]


def fallback_extract(resp: Any) -> str:
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        for key in ("response", "output", "reply", "text"):
            value = resp.get(key)
            if isinstance(value, str):
                return value
        message = resp.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            return message["content"]
        return json.dumps(resp)
    return str(resp)
