"""BGE-M3 embeddings via sentence-transformers."""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def load_embedder(model_name: str = "BAAI/bge-m3") -> SentenceTransformer:
    # trust_remote_code needed for some BGE builds; M3 works with ST out of the box
    return SentenceTransformer(model_name)


def embed_texts(
    texts: list[str],
    *,
    model_name: str = "BAAI/bge-m3",
    batch_size: int = 8,
    normalize: bool = True,
) -> list[list[float]]:
    """Embed passages. BGE retrieval docs recommend normalizing for cosine."""
    if not texts:
        return []
    model = load_embedder(model_name)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=normalize,
        show_progress_bar=len(texts) > 16,
    )
    return [v.tolist() for v in vectors]


def embed_query(
    query: str,
    *,
    model_name: str = "BAAI/bge-m3",
) -> list[float]:
    # BGE often uses an instruction prefix for queries; M3 dense works with raw query too.
    # Keep it simple for learning; we can add "Represent this sentence..." later if needed.
    return embed_texts([query], model_name=model_name, batch_size=1)[0]
