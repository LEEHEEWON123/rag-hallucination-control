"""Ingest local corpus into Qdrant with BGE-M3 embeddings."""

from __future__ import annotations

from grounding_pipeline.chunking import Chunk, chunk_markdown
from grounding_pipeline.config import Settings
from grounding_pipeline.corpus import load_corpus
from grounding_pipeline.embeddings import embed_texts
from grounding_pipeline.store import ensure_collection, get_client, upsert_chunks


def ingest_corpus(*, recreate: bool = True, settings: Settings | None = None) -> dict:
    settings = settings or Settings.from_env()
    docs = load_corpus(settings.corpus_dir)
    if not docs:
        raise RuntimeError(f"No markdown docs in {settings.corpus_dir}")

    chunks: list[Chunk] = []
    for doc in docs:
        rel = f"document/dobedub/{doc.path.name}"
        chunks.extend(
            chunk_markdown(
                doc.text,
                doc_id=doc.doc_id,
                source_path=rel,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
        )

    print(f"docs={len(docs)} chunks={len(chunks)} model={settings.embedding_model}")
    vectors = embed_texts([c.text for c in chunks], model_name=settings.embedding_model)

    client = get_client(settings)
    ensure_collection(client, settings, recreate=recreate)
    n = upsert_chunks(client, settings, chunks, vectors)
    info = client.get_collection(settings.collection)
    return {
        "docs": len(docs),
        "chunks": n,
        "collection": settings.collection,
        "points_count": info.points_count,
        "qdrant_url": settings.qdrant_url,
    }
