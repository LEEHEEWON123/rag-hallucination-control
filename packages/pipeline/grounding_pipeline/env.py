"""Load .env / .env.local from repo root (never commit secrets)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from grounding_pipeline.config import _repo_root


def load_env() -> None:
    root = _repo_root()
    # later files override earlier ones
    load_dotenv(root / ".env")
    load_dotenv(root / ".env.local", override=True)
