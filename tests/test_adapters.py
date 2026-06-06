from brechabot.adapters import get_adapter
from brechabot.models import ScanConfig

MESSAGES = [
    {"role": "system", "content": "SYS"},
    {"role": "user", "content": "u1"},
    {"role": "assistant", "content": "a1"},
    {"role": "user", "content": "u2"},
]


def cfg(schema: str) -> ScanConfig:
    return ScanConfig(target_url="https://t", schema=schema, target_model="m")


def test_openai_build_and_parse():
    a = get_adapter("openai")
    body = a.build_request(MESSAGES, cfg("openai"))
    assert body == {"model": "m", "messages": MESSAGES}
    assert a.parse_reply({"choices": [{"message": {"content": "hello"}}]}) == "hello"


def test_anthropic_build_and_parse():
    a = get_adapter("anthropic")
    body = a.build_request(MESSAGES, cfg("anthropic"))
    assert body["system"] == "SYS"
    assert body["messages"] == [
        {"role": "user", "content": "u1"},
        {"role": "assistant", "content": "a1"},
        {"role": "user", "content": "u2"},
    ]
    assert a.parse_reply({"content": [{"text": "h"}, {"text": "i"}]}) == "hi"


def test_cohere_build_and_parse():
    a = get_adapter("cohere")
    body = a.build_request(MESSAGES, cfg("cohere"))
    assert body["preamble"] == "SYS"
    assert body["message"] == "u2"
    assert body["chat_history"] == [
        {"role": "USER", "message": "u1"},
        {"role": "CHATBOT", "message": "a1"},
    ]
    assert a.parse_reply({"text": "ok"}) == "ok"


def test_rest_build_and_parse():
    a = get_adapter("rest")
    body = a.build_request(MESSAGES, cfg("rest"))
    assert body["system"] == "SYS"
    assert body["input"] == "u2"
    assert a.parse_reply({"output": "done"}) == "done"


def test_unknown_schema_falls_back_to_openai():
    assert get_adapter("nope").build_request(MESSAGES, cfg("openai"))["model"] == "m"
