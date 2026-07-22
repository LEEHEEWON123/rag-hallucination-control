"""Cite-forced generation prompts."""

from __future__ import annotations


REFUSAL_TEXT = "제공된 문서만으로는 답할 수 없습니다."


def build_cite_forced_prompt(question: str, numbered_chunks: list[tuple[int, dict]]) -> str:
    """Build a prompt that forces per-sentence [n] citations."""
    context_blocks: list[str] = []
    for n, hit in numbered_chunks:
        doc = hit.get("doc_id") or "unknown"
        text = (hit.get("text") or "").strip()
        context_blocks.append(f"[{n}] (doc={doc})\n{text}")

    context = "\n\n".join(context_blocks) if context_blocks else "(검색된 문맥 없음)"

    return f"""당신은 RAG 답변 생성기다. 코딩 에이전트가 아니다.
도구를 쓰지 말고, 파일을 읽거나 검색하지 마라. 아래 문맥만 보고 답하라.

규칙:
1. 아래 번호 매긴 문맥(CONTEXT)만 사용한다. 사전 지식·추측 금지.
2. 답변의 모든 문장 끝에 출처 번호 [n] 또는 [n, m]을 붙인다.
3. 문맥에 답이 없으면 정확히 다음 한 문장만 출력한다: {REFUSAL_TEXT}
4. 서론/요약/사과 없이 본문만 출력한다.
5. CONTEXT에 없는 번호는 인용하지 않는다.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""


def number_chunks(hits: list[dict]) -> list[tuple[int, dict]]:
    return [(i, hit) for i, hit in enumerate(hits, start=1)]
