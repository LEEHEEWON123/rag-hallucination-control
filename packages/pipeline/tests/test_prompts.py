from grounding_pipeline.prompts import REFUSAL_TEXT, build_cite_forced_prompt, number_chunks


def test_number_chunks_starts_at_one():
    numbered = number_chunks([{"text": "a"}, {"text": "b"}])
    assert [n for n, _ in numbered] == [1, 2]


def test_prompt_requires_citations_and_refusal():
    hits = [{"doc_id": "demo", "text": "시스템 코드는 BP-FE 이다."}]
    prompt = build_cite_forced_prompt("시스템 코드는?", number_chunks(hits))
    assert "[1] (doc=demo)" in prompt
    assert "[n]" in prompt or "출처 번호" in prompt
    assert REFUSAL_TEXT in prompt
    assert "도구를 쓰지 말고" in prompt
