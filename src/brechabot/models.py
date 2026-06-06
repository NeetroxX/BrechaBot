from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Verdict(StrEnum):
    VULNERABLE = "VULNERABLE"
    PARTIAL = "PARTIAL"
    SAFE = "SAFE"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"


class Severity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


def to_verdict(value: str) -> Verdict:
    try:
        return Verdict(value)
    except ValueError:
        return Verdict.UNKNOWN


def to_severity(value: str) -> Severity:
    try:
        return Severity(value)
    except ValueError:
        return Severity.NONE


class Attack(BaseModel):
    id: str
    category: str
    name: str
    technique: str = ""
    severity: Severity = Severity.MEDIUM
    prompt: str | None = None
    turns: list[str] | None = None
    markers: list[str] = Field(default_factory=list)
    lang: str = "en"

    @model_validator(mode="after")
    def _exactly_one_prompt_form(self) -> Attack:
        has_prompt = self.prompt is not None
        has_turns = bool(self.turns)
        if has_prompt == has_turns:
            raise ValueError(f"{self.id}: provide exactly one of 'prompt' or 'turns'")
        return self

    @property
    def turn_list(self) -> list[str]:
        return list(self.turns) if self.turns else [self.prompt or ""]

    @property
    def is_multi_turn(self) -> bool:
        return self.turns is not None and len(self.turns) > 1


class JudgeConfig(BaseModel):
    base_url: str = "http://localhost:11434/v1"
    model: str = "gemma4:31b-cloud"
    api_key: str | None = None
    temperature: float = 0.0


Schema = Literal["openai", "anthropic", "cohere", "rest"]


class ScanConfig(BaseModel):
    model_config = {"populate_by_name": True}

    target_url: str
    target_schema: Schema = Field("openai", alias="schema")
    target_model: str = "gpt-4o-mini"
    system_prompt: str = "You are a helpful assistant."
    auth_header: str | None = None
    judge: JudgeConfig = Field(default_factory=JudgeConfig)
    profile: str = "full"
    concurrency: int = 4
    timeout_s: float = 90.0
    max_retries: int = 2


class TranscriptTurn(BaseModel):
    turn: int
    user: str
    bot: str


class Finding(BaseModel):
    id: str
    name: str
    category: str
    technique: str
    owasp: str
    remediation: str
    lang: str
    is_multi_turn: bool
    transcript: list[TranscriptTurn]
    attack_prompt: str
    bot_reply: str
    verdict: Verdict
    severity: Severity
    reason: str
    marker_matches: list[str] = Field(default_factory=list)
    judge_verdict: str = "UNKNOWN"
    judge_severity: str = "none"


class ScanResult(BaseModel):
    model_config = {"populate_by_name": True}

    scan_id: str = Field(serialization_alias="scanId")
    corpus_version: str
    started_at: str
    finished_at: str
    summary: dict
    findings: list[Finding]
    html: str
