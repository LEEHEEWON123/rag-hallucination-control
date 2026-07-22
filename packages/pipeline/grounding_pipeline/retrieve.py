"""Retrieve (+ optional re-rank) top-k chunks from Qdrant."""

from __future__ import annotations

from grounding_pipeline.config import Settings
from grounding_pipeline.embeddings import embed_query
from grounding_pipeline.rerank import rerank
from grounding_pipeline.store import get_client, search


def retrieve(
    query: str,
    *,
    top_k: int | None = None,
    candidate_k: int | None = None,
    use_rerank: bool | None = None,
    settings: Settings | None = None,
) -> list[dict]:
    """
    1) Dense retrieve `candidate_k` from Qdrant
    2) Cross-encoder re-rank → keep `top_k` (unless use_rerank=False)
    """
    settings = settings or Settings.from_env()
    final_k = top_k if top_k is not None else settings.top_k
    cand_k = candidate_k if candidate_k is not None else settings.candidate_k
    do_rerank = settings.use_rerank if use_rerank is None else use_rerank

    if do_rerank and cand_k < final_k:
        cand_k = final_k

    vector = embed_query(query, model_name=settings.embedding_model)
    client = get_client(settings)
    hits = search(client, settings, vector, top_k=cand_k if do_rerank else final_k)

    if not do_rerank:
        for hit in hits:
            hit["vector_score"] = float(hit.get("score") or 0.0)
            hit["rerank_score"] = None
        return hits

    return rerank(
        query,
        hits,
        top_k=final_k,
        model_name=settings.rerank_model,
    )
