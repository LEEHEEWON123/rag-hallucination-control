from grounding_pipeline.claims import parse_citation_ns, split_claims, strip_citations
from grounding_pipeline.prompts import REFUSAL_TEXT
from grounding_pipeline.verify import apply_gate


def test_parse_citations():
    assert parse_citation_ns("코드는 BP-FE다. [1]") == (1,)
    assert parse_citation_ns("A [1][2] B [2, 3]") == (1, 2, 3)


def test_split_claims_keeps_raw_with_citation():
    answer = "시스템 코드는 BP-FE이다. [1] Vue를 쓴다. [2]"
    claims = split_claims(answer)
    assert len(claims) == 2
    assert claims[0].citation_ns == (1,)
    assert "BP-FE" in claims[0].text
    assert "[1]" in claims[0].raw
    assert strip_citations(claims[0].raw) == claims[0].text


def test_apply_gate_drops_unsupported():
    results = [
        {"raw": "좋은 문장. [1]", "label": "supported", "claim": "좋은 문장.", "citations": [1]},
        {"raw": "거짓. [2]", "label": "unsupported", "claim": "거짓.", "citations": [2]},
        {"raw": "인용없음.", "label": "uncited", "claim": "인용없음.", "citations": []},
    ]
    gated = apply_gate(results)
    assert gated["refused"] is False
    assert gated["final_answer"] == "좋은 문장. [1]"
    assert len(gated["dropped"]) == 2


def test_apply_gate_refuses_when_empty():
    results = [
        {"raw": "거짓. [1]", "label": "unsupported", "claim": "거짓.", "citations": [1]},
    ]
    gated = apply_gate(results)
    assert gated["refused"] is True
    assert gated["final_answer"] == REFUSAL_TEXT
