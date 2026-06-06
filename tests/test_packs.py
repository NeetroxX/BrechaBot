import json
from pathlib import Path

import pytest

from brechabot.corpus import loader


def test_load_starter_builtin():
    pack = loader.load_pack("starter")
    assert pack.id == "starter"
    assert len(pack.attacks) == 10


def test_load_corpus_default_is_starter():
    corpus = loader.load_corpus()
    assert len(corpus.attacks) == 10
    assert corpus.version.startswith("brc-")
    assert corpus.packs == ["starter@1.0.0"]


def test_env_default(monkeypatch):
    monkeypatch.setenv("BRECHABOT_PACK", "starter")
    assert loader.default_refs() == ["starter"]
    monkeypatch.delenv("BRECHABOT_PACK")
    assert loader.default_refs() == ["starter"]


def test_merge_two_packs(tmp_path):
    extra = tmp_path / "extra"
    extra.mkdir()
    (extra / "pack.json").write_text(
        json.dumps({"id": "extra", "name": "Extra", "version": "0.1.0"}), encoding="utf-8"
    )
    (extra / "attacks.json").write_text(
        json.dumps([{"id": "ZZZ-1", "category": "Custom", "name": "X", "prompt": "hi", "markers": ["a"]}]),
        encoding="utf-8",
    )
    (extra / "categories.json").write_text(
        json.dumps({"Custom": {"owasp": "LLM01", "remediation": "r"}}), encoding="utf-8"
    )

    corpus = loader.load_corpus(["starter", str(extra)])
    ids = {a.id for a in corpus.attacks}
    assert "ZZZ-1" in ids and len(corpus.attacks) == 11
    assert "Custom" in corpus.categories
    assert corpus.packs == ["starter@1.0.0", "extra@0.1.0"]


def test_unknown_pack_raises():
    with pytest.raises(FileNotFoundError):
        loader.load_pack(str(Path("does-not-exist")))
