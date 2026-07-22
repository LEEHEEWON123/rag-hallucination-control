"""Cross-encoder re-rank over retrieved candidates (BGE-reranker)."""

from __future__ import annotations

from functools import lru_cache

from sentence_transformers import CrossEncoder


@lru_cache(maxsize=1)
def load_reranker(model_name: str = "BAAI/bge-reranker-v2-m3") -> CrossEncoder:
    return CrossEncoder(model_name)


def rerank(
    query: str,
    hits: list[dict],
    *,
    top_k: int = 5,
    model_name: str = "BAAI/bge-reranker-v2-m3",
) -> list[dict]:
    """Re-score (query, passage) pairs and keep the best top_k."""
    if not hits:
        return []

    model = load_reranker(model_name)
    pairs = [(query, hit.get("text") or "") for hit in hits]
    scores = model.predict(pairs)

    ranked: list[dict] = []
    for hit, score in zip(hits, scores, strict=True):
        item = dict(hit)
        item["vector_score"] = float(hit.get("score") or 0.0)
        item["rerank_score"] = float(score)
        item["score"] = float(score)  # primary score after rerank
        ranked.append(item)

    ranked.sort(key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]
