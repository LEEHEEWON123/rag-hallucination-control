from grounding_pipeline.rerank import rerank


def test_rerank_orders_by_score(monkeypatch):
    class FakeModel:
        def predict(self, pairs):
            # higher when passage mentions exact keyword
            return [1.0 if "정답" in p[1] else 0.1 for p in pairs]

    monkeypatch.setattr("grounding_pipeline.rerank.load_reranker", lambda model_name="x": FakeModel())

    hits = [
        {"text": "관련 없는 이야기", "score": 0.9, "doc_id": "a", "chunk_id": "a::0"},
        {"text": "여기에 정답 키워드", "score": 0.5, "doc_id": "b", "chunk_id": "b::0"},
    ]
    out = rerank("질문", hits, top_k=1, model_name="fake")
    assert len(out) == 1
    assert out[0]["doc_id"] == "b"
    assert out[0]["rerank_score"] == 1.0
    assert out[0]["vector_score"] == 0.5
