"""Split answers into claims and parse [n] citations."""

from __future__ import annotations

import re
from dataclasses import dataclass

from grounding_pipeline.prompts import REFUSAL_TEXT

_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
# Keep trailing citations with the sentence: "문장이다. [1][2]"
_CLAIM_PIECE = re.compile(
    r"[^.!?。\n]+(?:[.!?。]+)?(?:\s*\[\d+(?:\s*,\s*\d+)*\])*",
    re.UNICODE,
)


@dataclass(frozen=True)
class Claim:
    text: str
    citation_ns: tuple[int, ...]
    raw: str


def is_refusal_answer(answer: str) -> bool:
    cleaned = (answer or "").strip()
    return cleaned == REFUSAL_TEXT or REFUSAL_TEXT in cleaned


def parse_citation_ns(text: str) -> tuple[int, ...]:
    found: list[int] = []
    for match in _CITATION.finditer(text):
        for part in match.group(1).split(","):
            part = part.strip()
            if part.isdigit():
                n = int(part)
                if n not in found:
                    found.append(n)
    return tuple(found)


def strip_citations(text: str) -> str:
    return _CITATION.sub("", text).strip()


def split_claims(answer: str) -> list[Claim]:
    """Split answer into sentence-level claims with citation numbers."""
    cleaned = (answer or "").strip()
    if not cleaned:
        return []

    parts = [p.strip() for p in _CLAIM_PIECE.findall(cleaned) if p and p.strip()]
    if not parts:
        parts = [cleaned]

    claims: list[Claim] = []
    for part in parts:
        ns = parse_citation_ns(part)
        body = strip_citations(part)
        # Drop orphan citation-only leftovers, if any.
        if not body:
            if ns and claims:
                prev = claims[-1]
                merged_ns = tuple(dict.fromkeys([*prev.citation_ns, *ns]))
                claims[-1] = Claim(
                    text=prev.text,
                    citation_ns=merged_ns,
                    raw=f"{prev.raw} {part}".strip(),
                )
            continue
        claims.append(Claim(text=body, citation_ns=ns, raw=part))
    return claims
