# grounding-pipeline

Claim-level grounding guard의 **핵심 로직** 패키지.

## 현재 구현

1. `chunking` — 마크다운 청크
2. `embeddings` — BGE-M3 (`sentence-transformers`)
3. `ingest` — 코퍼스 → Qdrant
4. `retrieve` — dense 검색
5. `rerank` — BGE-reranker-v2-m3 cross-encoder

아직 없는 것: cite-forced generate, claim verify, refusal.

## 실행

repo root에서 Qdrant 띄운 뒤:

```bash
docker compose up -d
source .venv/bin/activate
pip install -e "packages/pipeline[dev]"
python -m grounding_pipeline ingest
python -m grounding_pipeline retrieve "덥라이트 기술 스택은?" -k 3
python -m grounding_pipeline retrieve "덥라이트 기술 스택은?" -k 3 --no-rerank
```
