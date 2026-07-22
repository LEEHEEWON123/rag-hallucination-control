"""Load corpus markdown files (skip README)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Document:
    doc_id: str
    path: Path
    text: str


def load_corpus(corpus_dir: Path) -> list[Document]:
    if not corpus_dir.exists():
        raise FileNotFoundError(
            f"Corpus not found: {corpus_dir}. Run scripts/sync_dobedub_corpus.sh first."
        )

    docs: list[Document] = []
    for path in sorted(corpus_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8")
        docs.append(Document(doc_id=path.stem, path=path, text=text))
    return docs
