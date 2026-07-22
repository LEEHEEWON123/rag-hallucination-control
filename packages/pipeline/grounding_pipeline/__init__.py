"""Claim-level grounding guard pipeline."""

__version__ = "0.1.0"


def health() -> dict[str, str]:
    """Smoke-check used by the API scaffold."""
    return {"package": "grounding-pipeline", "status": "ok"}
