from __future__ import annotations

from .anthropic import AnthropicAdapter
from .base import TargetAdapter
from .cohere import CohereAdapter
from .openai import OpenAIAdapter
from .rest import RestAdapter

_ADAPTERS: dict[str, TargetAdapter] = {
    "openai": OpenAIAdapter(),
    "anthropic": AnthropicAdapter(),
    "cohere": CohereAdapter(),
    "rest": RestAdapter(),
}


def get_adapter(schema: str) -> TargetAdapter:
    return _ADAPTERS.get(schema, _ADAPTERS["openai"])
