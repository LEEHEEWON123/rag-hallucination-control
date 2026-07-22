"""Cite-forced answer generation via Cursor SDK."""

from __future__ import annotations

from grounding_pipeline.config import Settings
from grounding_pipeline.cursor_llm import run_cursor_prompt
from grounding_pipeline.prompts import REFUSAL_TEXT, build_cite_forced_prompt, number_chunks
from grounding_pipeline.retrieve import retrieve
from grounding_pipeline.verify import verify_and_gate


def generate_cited_answer(
    question: str,
    hits: list[dict],
    *,
    settings: Settings | None = None,
) -> dict:
    """Generate an answer that must cite numbered retrieved chunks."""
    settings = settings or Settings.from_env()
    numbered = number_chunks(hits)
    prompt = build_cite_forced_prompt(question, numbered)
    answer = run_cursor_prompt(prompt, model=settings.cursor_model)

    return {
        "question": question,
        "answer": answer,
        "refused": answer == REFUSAL_TEXT or REFUSAL_TEXT in answer,
        "chunks": [
            {
                "n": n,
                "doc_id": hit.get("doc_id"),
                "chunk_id": hit.get("chunk_id"),
                "score": hit.get("score"),
                "rerank_score": hit.get("rerank_score"),
                "vector_score": hit.get("vector_score"),
                "text": hit.get("text"),
            }
            for n, hit in numbered
        ],
        "model": settings.cursor_model,
    }


def ask(
    question: str,
    *,
    top_k: int | None = None,
    candidate_k: int | None = None,
    use_rerank: bool | None = None,
    guard: bool = True,
    settings: Settings | None = None,
) -> dict:
    """Retrieve (+ rerank) → cite-forced generate → optional claim verify gate."""
    settings = settings or Settings.from_env()
    hits = retrieve(
        question,
        top_k=top_k,
        candidate_k=candidate_k,
        use_rerank=use_rerank,
        settings=settings,
    )
    generated = generate_cited_answer(question, hits, settings=settings)
    verification = verify_and_gate(
        generated["answer"],
        generated["chunks"],
        settings=settings,
        enabled=guard,
    )
    return {
        **generated,
        "draft_answer": verification["draft_answer"],
        "answer": verification["final_answer"],
        "refused": verification["refused"],
        "guard": verification["enabled"],
        "claims": verification["claims"],
        "kept": verification["kept"],
        "dropped": verification["dropped"],
    }
