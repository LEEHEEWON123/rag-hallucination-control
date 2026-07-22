"""Claim-level faithfulness verify + refusal gate."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from grounding_pipeline.claims import Claim, is_refusal_answer, split_claims
from grounding_pipeline.config import Settings
from grounding_pipeline.cursor_llm import run_cursor_prompt
from grounding_pipeline.prompts import REFUSAL_TEXT

Label = Literal["supported", "partial", "unsupported", "uncited"]
_KEEP_DEFAULT: set[str] = {"supported", "partial"}
_JSON_BLOCK = re.compile(r"\{[\s\S]*\}|\[[\s\S]*\]")


def _chunk_map(chunks: list[dict]) -> dict[int, dict]:
    return {int(c["n"]): c for c in chunks if c.get("n") is not None}


def _build_judge_prompt(claims: list[Claim], chunks_by_n: dict[int, dict]) -> str:
    items: list[dict[str, Any]] = []
    for i, claim in enumerate(claims):
        evidence = []
        for n in claim.citation_ns:
            chunk = chunks_by_n.get(n)
            evidence.append(
                {
                    "n": n,
                    "text": (chunk or {}).get("text") or "",
                    "missing": chunk is None,
                }
            )
        items.append(
            {
                "id": i,
                "claim": claim.text,
                "citations": list(claim.citation_ns),
                "evidence": evidence,
            }
        )

    return f"""당신은 RAG faithfulness 판정기다. 코딩 에이전트가 아니다.
도구/파일 사용 금지. 아래 JSON 배열만 출력한다.

각 항목에 대해 claim이 evidence 텍스트로 지지되는지 판정하라.
라벨은 정확히 하나만: supported | partial | unsupported | uncited
- supported: evidence가 claim을 명확히 지지
- partial: 관련은 있으나 과장/누락/애매
- unsupported: 인용은 있으나 evidence가 claim을 지지하지 않음 (또는 missing citation)
- uncited: 인용이 비어 있음

입력:
{json.dumps(items, ensure_ascii=False, indent=2)}

출력 형식(JSON only):
[
  {{"id": 0, "label": "supported", "reason": "짧은 한국어 이유"}}
]
"""


def _parse_judge_json(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = _JSON_BLOCK.search(text)
    if not match:
        raise ValueError(f"Judge returned non-JSON: {raw[:200]}")
    data = json.loads(match.group(0))
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    if not isinstance(data, list):
        raise ValueError("Judge JSON must be a list")
    return data


def _local_prelabel(claim: Claim, chunks_by_n: dict[int, dict]) -> Label | None:
    if not claim.citation_ns:
        return "uncited"
    if any(n not in chunks_by_n for n in claim.citation_ns):
        return "unsupported"
    return None


def judge_claims(
    claims: list[Claim],
    chunks: list[dict],
    *,
    settings: Settings | None = None,
) -> list[dict]:
    settings = settings or Settings.from_env()
    chunks_by_n = _chunk_map(chunks)
    if not claims:
        return []

    # Fast path labels that don't need an LLM.
    prelim: dict[int, dict] = {}
    need_judge: list[tuple[int, Claim]] = []
    for i, claim in enumerate(claims):
        pre = _local_prelabel(claim, chunks_by_n)
        if pre is not None:
            prelim[i] = {
                "id": i,
                "claim": claim.text,
                "citations": list(claim.citation_ns),
                "label": pre,
                "reason": "규칙 기반 사전 판정",
                "raw": claim.raw,
            }
        else:
            need_judge.append((i, claim))

    judged: dict[int, dict] = dict(prelim)
    if need_judge:
        only_claims = [c for _, c in need_judge]
        raw = run_cursor_prompt(
            _build_judge_prompt(only_claims, chunks_by_n),
            model=settings.cursor_model,
        )
        parsed = _parse_judge_json(raw)
        # Map back: judge ids are 0..len(need_judge)-1 relative to only_claims
        for row in parsed:
            local_id = int(row["id"])
            if local_id < 0 or local_id >= len(need_judge):
                continue
            global_id, claim = need_judge[local_id]
            label = str(row.get("label", "unsupported")).lower().strip()
            if label not in {"supported", "partial", "unsupported", "uncited"}:
                label = "unsupported"
            judged[global_id] = {
                "id": global_id,
                "claim": claim.text,
                "citations": list(claim.citation_ns),
                "label": label,
                "reason": str(row.get("reason") or ""),
                "raw": claim.raw,
            }

        # Any claim missing from judge output → unsupported
        for global_id, claim in need_judge:
            if global_id not in judged:
                judged[global_id] = {
                    "id": global_id,
                    "claim": claim.text,
                    "citations": list(claim.citation_ns),
                    "label": "unsupported",
                    "reason": "판정 결과 누락",
                    "raw": claim.raw,
                }

    return [judged[i] for i in range(len(claims))]


def apply_gate(
    claim_results: list[dict],
    *,
    keep_labels: set[str] | None = None,
) -> dict:
    keep = keep_labels or set(_KEEP_DEFAULT)
    kept = [c for c in claim_results if c.get("label") in keep]
    dropped = [c for c in claim_results if c.get("label") not in keep]

    if kept:
        final = " ".join(c["raw"] for c in kept).strip()
        refused = False
    else:
        final = REFUSAL_TEXT
        refused = True

    return {
        "final_answer": final,
        "refused": refused,
        "kept": kept,
        "dropped": dropped,
    }


def verify_and_gate(
    answer: str,
    chunks: list[dict],
    *,
    settings: Settings | None = None,
    enabled: bool = True,
) -> dict:
    """Verify claims against cited chunks and filter unsupported ones."""
    if not enabled:
        return {
            "enabled": False,
            "draft_answer": answer,
            "final_answer": answer,
            "refused": is_refusal_answer(answer),
            "claims": [],
            "kept": [],
            "dropped": [],
        }

    if is_refusal_answer(answer):
        return {
            "enabled": True,
            "draft_answer": answer,
            "final_answer": REFUSAL_TEXT,
            "refused": True,
            "claims": [],
            "kept": [],
            "dropped": [],
        }

    claims = split_claims(answer)
    claim_results = judge_claims(claims, chunks, settings=settings)
    gated = apply_gate(claim_results)
    return {
        "enabled": True,
        "draft_answer": answer,
        "final_answer": gated["final_answer"],
        "refused": gated["refused"],
        "claims": claim_results,
        "kept": gated["kept"],
        "dropped": gated["dropped"],
    }
