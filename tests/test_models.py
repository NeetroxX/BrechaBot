import pytest
from pydantic import ValidationError

from brechabot.models import (
    Attack,
    ScanConfig,
    Severity,
    Verdict,
    to_severity,
    to_verdict,
)


def test_single_turn_attack_ok():
    a = Attack(id="PXR-001", category="Role Hijacking", name="X", prompt="hi", markers=["a"])
    assert a.is_multi_turn is False
    assert a.turn_list == ["hi"]


def test_multi_turn_attack_ok():
    a = Attack(id="PXR-046", category="Multi-Turn", name="Y", turns=["t1", "t2"])
    assert a.is_multi_turn is True
    assert a.turn_list == ["t1", "t2"]


def test_attack_requires_exactly_one_prompt_form():
    with pytest.raises(ValidationError):
        Attack(id="PXR-X", category="C", name="N")  # neither
    with pytest.raises(ValidationError):
        Attack(id="PXR-Y", category="C", name="N", prompt="p", turns=["t"])  # both


def test_scan_config_schema_alias():
    cfg = ScanConfig(target_url="https://x", schema="anthropic")
    assert cfg.target_schema == "anthropic"


def test_coercion_helpers():
    assert to_verdict("VULNERABLE") is Verdict.VULNERABLE
    assert to_verdict("garbage") is Verdict.UNKNOWN
    assert to_severity("high") is Severity.HIGH
    assert to_severity("garbage") is Severity.NONE
