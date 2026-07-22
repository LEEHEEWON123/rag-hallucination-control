"""Thin Cursor SDK prompt helper (isolated empty cwd)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions, SandboxOptions

from grounding_pipeline.env import load_env


def run_cursor_prompt(prompt: str, *, model: str) -> str:
    load_env()
    api_key = os.getenv("CURSOR_API_KEY")
    if not api_key:
        raise RuntimeError("CURSOR_API_KEY is missing. Set it in .env.local")

    workdir = Path(tempfile.mkdtemp(prefix="grounding-cursor-"))
    (workdir / "README.txt").write_text(
        "Empty workspace. Do not use tools. Follow the prompt only.\n",
        encoding="utf-8",
    )

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(
                    cwd=str(workdir),
                    sandbox_options=SandboxOptions(enabled=True),
                ),
            ),
        )
    except CursorAgentError as err:
        raise RuntimeError(f"Cursor agent failed to start: {err}") from err

    if result.status == "error":
        raise RuntimeError(f"Cursor agent run failed: id={result.id}")

    return (result.result or "").strip()
