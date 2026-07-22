"""Qdrant helpers for the dobedub collection."""

from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from grounding_pipeline.chunking import Chunk
from grounding_pipeline.config import Settings


def get_client(settings: Settings | None = None) -> QdrantClient:
    settings = settings or Settings.from_env()
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(client: QdrantClient, settings: Settings, *, recreate: bool = False) -> None:
    exists = client.collection_exists(settings.collection)
    if exists and recreate:
        client.delete_collection(settings.collection)
        exists = False
    if not exists:
        client.create_collection(
            collection_name=settings.collection,
            vectors_config=qm.VectorParams(
                size=settings.vector_size,
                distance=qm.Distance.COSINE,
            ),
        )


def upsert_chunks(
    client: QdrantClient,
    settings: Settings,
    chunks: list[Chunk],
    vectors: list[list[float]],
) -> int:
    if len(chunks) != len(vectors):
        raise ValueError("chunks and vectors length mismatch")

    points = [
        qm.PointStruct(
            id=_stable_id(chunk.chunk_id),
            vector=vector,
            payload={
                "doc_id": chunk.doc_id,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_path": chunk.source_path,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            },
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]

    # upsert in batches to keep memory sane
    batch = 64
    for i in range(0, len(points), batch):
        client.upsert(collection_name=settings.collection, points=points[i : i + batch])
    return len(points)


def search(
    client: QdrantClient,
    settings: Settings,
    query_vector: list[float],
    *,
    top_k: int = 5,
) -> list[dict]:
    hits = client.query_points(
        collection_name=settings.collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    results: list[dict] = []
    for hit in hits:
        payload = hit.payload or {}
        results.append(
            {
                "score": float(hit.score) if hit.score is not None else 0.0,
                "doc_id": payload.get("doc_id"),
                "chunk_id": payload.get("chunk_id"),
                "text": payload.get("text"),
                "source_path": payload.get("source_path"),
                "start_char": payload.get("start_char"),
                "end_char": payload.get("end_char"),
            }
        )
    return results


def _stable_id(chunk_id: str) -> int:
    # Qdrant accepts unsigned int or UUID; hash to stable positive int
    import hashlib

    digest = hashlib.md5(chunk_id.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) % (2**63)
