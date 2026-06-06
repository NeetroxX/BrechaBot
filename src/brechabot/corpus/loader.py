from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from pydantic import BaseModel

from ..models import Attack

_PACKS_DIR = Path(__file__).parent.parent / "packs"
BUILTIN_PACKS: dict[str, Path] = {"starter": _PACKS_DIR / "starter"}


class Pack(BaseModel):
    id: str
    name: str
    version: str
    attacks: list[Attack]
    categories: dict[str, dict[str, str]]


class Corpus(BaseModel):
    attacks: list[Attack]
    categories: dict[str, dict[str, str]]
    packs: list[str]
    version: str


def _resolve(ref: str) -> Path:
    if ref in BUILTIN_PACKS:
        return BUILTIN_PACKS[ref]
    path = Path(ref)
    if not path.exists():
        raise FileNotFoundError(f"pack not found: {ref}")
    return path


def load_pack(ref: str) -> Pack:
    d = _resolve(ref)
    meta = json.loads((d / "pack.json").read_text(encoding="utf-8"))
    attacks = [Attack.model_validate(a) for a in json.loads((d / "attacks.json").read_text(encoding="utf-8"))]
    categories = json.loads((d / "categories.json").read_text(encoding="utf-8"))
    return Pack(
        id=meta["id"], name=meta["name"], version=meta["version"],
        attacks=attacks, categories=categories,
    )


def default_refs() -> list[str]:
    env = os.environ.get("BRECHABOT_PACK")
    if env:
        return [r.strip() for r in env.split(",") if r.strip()]
    return ["starter"]


def load_corpus(refs: list[str] | None = None) -> Corpus:
    refs = refs or default_refs()
    merged_attacks: dict[str, Attack] = {}
    merged_categories: dict[str, dict[str, str]] = {}
    pack_ids: list[str] = []
    hasher = hashlib.sha256()
    for ref in refs:
        d = _resolve(ref)
        for name in ("pack.json", "categories.json", "attacks.json"):
            hasher.update((d / name).read_bytes())
        pack = load_pack(ref)
        pack_ids.append(f"{pack.id}@{pack.version}")
        merged_categories.update(pack.categories)
        for attack in pack.attacks:
            merged_attacks[attack.id] = attack
    return Corpus(
        attacks=list(merged_attacks.values()),
        categories=merged_categories,
        packs=pack_ids,
        version="brc-" + hasher.hexdigest()[:12],
    )


def owasp_for(category: str, categories: dict[str, dict[str, str]]) -> str:
    return categories.get(category, {}).get("owasp", "")


def remediation_for(category: str, categories: dict[str, dict[str, str]]) -> str:
    return categories.get(category, {}).get("remediation", "")
