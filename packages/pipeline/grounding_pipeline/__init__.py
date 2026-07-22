"""Claim-level grounding guard pipeline."""

__version__ = "0.1.0"

from grounding_pipeline.generate import ask, generate_cited_answer
from grounding_pipeline.ingest import ingest_corpus
from grounding_pipeline.retrieve import retrieve
from grounding_pipeline.verify import verify_and_gate


def health() -> dict[str, str]:
    """Smoke-check used by the API scaffold."""
    return {"package": "grounding-pipeline", "status": "ok", "version": __version__}


__all__ = [
    "health",
    "ingest_corpus",
    "retrieve",
    "ask",
    "generate_cited_answer",
    "verify_and_gate",
    "__version__",
]
