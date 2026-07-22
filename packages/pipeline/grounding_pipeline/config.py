"""Shared settings for ingest / retrieve."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    # packages/pipeline/grounding_pipeline/config.py → repo root
    return Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    qdrant_url: str = "http://localhost:6333"
    collection: str = "dobedub_docs"
    corpus_dir: Path = _repo_root() / "document" / "dobedub"
    embedding_model: str = "BAAI/bge-m3"
    # BGE-M3 dense output dim
    vector_size: int = 1024
    chunk_size: int = 800
    chunk_overlap: int = 120
    # retrieve broadly, then re-rank down
    candidate_k: int = 20
    top_k: int = 5
    use_rerank: bool = True
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    cursor_model: str = "composer-2.5"

    @classmethod
    def from_env(cls) -> "Settings":
        root = _repo_root()
        corpus = os.getenv("CORPUS_DIR", "document/dobedub")
        corpus_path = Path(corpus)
        if not corpus_path.is_absolute():
            corpus_path = root / corpus_path
        return cls(
            qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            collection=os.getenv("QDRANT_COLLECTION", "dobedub_docs"),
            corpus_dir=corpus_path,
            embedding_model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
            chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
            candidate_k=int(os.getenv("CANDIDATE_K", "20")),
            top_k=int(os.getenv("TOP_K", "5")),
            use_rerank=os.getenv("USE_RERANK", "true").lower() in {"1", "true", "yes"},
            rerank_model=os.getenv("RERANK_MODEL", "BAAI/bge-reranker-v2-m3"),
            cursor_model=os.getenv("CURSOR_MODEL", "composer-2.5"),
        )
