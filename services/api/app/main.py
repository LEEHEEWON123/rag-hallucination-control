from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from grounding_pipeline import ask as pipeline_ask
from grounding_pipeline import health as pipeline_health
from grounding_pipeline.env import load_env

load_env()

app = FastAPI(title="Grounding Guard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(min_length=1)
    guard: bool = True
    top_k: int = Field(default=5, ge=1, le=20)
    candidate_k: int = Field(default=20, ge=1, le=50)
    use_rerank: bool = True


class AskResponse(BaseModel):
    question: str
    answer: str
    draft_answer: str | None = None
    refused: bool
    guard: bool
    claims: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    model: str | None = None


@app.get("/health")
def health():
    return {
        "api": "ok",
        "pipeline": pipeline_health(),
    }


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    try:
        result = pipeline_ask(
            body.question,
            top_k=body.top_k,
            candidate_k=body.candidate_k,
            use_rerank=body.use_rerank,
            guard=body.guard,
        )
    except Exception as exc:  # noqa: BLE001 - surface pipeline errors to demo UI
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskResponse(
        question=result.get("question", body.question),
        answer=result.get("answer", ""),
        draft_answer=result.get("draft_answer"),
        refused=bool(result.get("refused")),
        guard=bool(result.get("guard")),
        claims=result.get("claims") or [],
        kept=result.get("kept") or [],
        dropped=result.get("dropped") or [],
        chunks=result.get("chunks") or [],
        model=result.get("model"),
    )
