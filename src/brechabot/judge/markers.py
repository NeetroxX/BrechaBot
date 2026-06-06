from __future__ import annotations

import re

_REFUSAL = re.compile(
    r"(i'?m sorry|i cannot|i can'?t|unable to|not able to|i won'?t"
    r"|against (my|the) (policy|guidelines))",
    re.IGNORECASE,
)


def marker_matches(reply: str, markers: list[str]) -> list[str]:
    hits: list[str] = []
    for marker in markers:
        try:
            if re.search(marker, reply, re.IGNORECASE):
                hits.append(marker)
        except re.error:
            continue
    return hits


def looks_like_refusal(reply: str) -> bool:
    return bool(_REFUSAL.search(reply)) and len(reply) < 400
