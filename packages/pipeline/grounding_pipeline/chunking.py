"""Split markdown docs into overlapping text chunks."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    chunk_id: str
    text: str
    source_path: str
    start_char: int
    end_char: int


_HEADING = re.compile(r"(?m)^(#{1,6}\s+.+)$")


def chunk_markdown(
    text: str,
    *,
    doc_id: str,
    source_path: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[Chunk]:
    """Chunk by size, preferring breaks near blank lines / headings."""
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    pieces: list[tuple[int, int, str]] = []
    start = 0
    n = len(cleaned)

    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            window = cleaned[start:end]
            # prefer split on blank line, then heading, then newline
            cut = window.rfind("\n\n")
            if cut < chunk_size * 0.4:
                heading_cuts = [m.start() for m in _HEADING.finditer(window)]
                cut = heading_cuts[-1] if heading_cuts else window.rfind("\n")
            if cut >= chunk_size * 0.4:
                end = start + cut

        piece = cleaned[start:end].strip()
        if piece:
            pieces.append((start, end, piece))

        if end >= n:
            break
        start = max(end - chunk_overlap, start + 1)

    return [
        Chunk(
            doc_id=doc_id,
            chunk_id=f"{doc_id}::{i}",
            text=piece,
            source_path=source_path,
            start_char=s,
            end_char=e,
        )
        for i, (s, e, piece) in enumerate(pieces)
    ]
