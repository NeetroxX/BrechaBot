from __future__ import annotations

from typing import Any

from .base import Message, fallback_extract, non_system, system_of


class CohereAdapter:
    def build_request(self, messages: list[Message], cfg: Any) -> dict[str, Any]:
        convo = non_system(messages)
        history = convo[:-1]
        last = convo[-1]["content"] if convo else ""
        chat_history = [
            {"role": "USER" if m["role"] == "user" else "CHATBOT", "message": m["content"]}
            for m in history
        ]
        return {
            "model": cfg.target_model,
            "preamble": system_of(messages),
            "chat_history": chat_history,
            "message": last,
        }

    def parse_reply(self, resp: Any) -> str:
        if isinstance(resp, dict):
            if isinstance(resp.get("text"), str):
                return resp["text"]
            message = resp.get("message")
            if isinstance(message, dict):
                content = message.get("content")
                if isinstance(content, list) and content and isinstance(content[0], dict):
                    return content[0].get("text", "")
        return fallback_extract(resp)
