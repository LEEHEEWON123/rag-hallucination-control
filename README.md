# RAG Hallucination Control

포트폴리오 프로젝트: RAG 답변을 위한 **Claim-level Grounding Guard**.

RAG는 문서를 검색할 뿐, 할루시에이션을 막아주지는 않습니다. 이 프로젝트는 답변의 각 claim이 인용된 출처 청크와 맞는지 검사하고, 근거 없거나 잘못된 인용은 걸러내거나 거절합니다. 데모 UI에서 통제 ON/OFF와 claim 판정 색을 보여줍니다.

## 한눈에 보는 파이프라인

```
질문
  → dense retrieve (BGE-M3 + Qdrant)
  → re-rank (BGE-reranker-v2-m3)
  → 청크에 [1][2]… 슬롯 부여
  → cite-forced generate (Cursor SDK)  # 문장마다 [n] 주석
  → claim verify + gate                 # 문장 ↔ 인용 청크 비교
  → 최종 답 / 거절
```

| 단계 | 비교 대상 | 역할 |
|------|-----------|------|
| retrieve / re-rank | 질문 ↔ 청크 | 관련 후보 고르기 |
| cite-forced generate | 청크로 답 작성 | 검증 가능한 형식 강제 |
| claim verify | **답 문장 ↔ 인용 청크** | 할루시에이션 통제 |

## 스택

| 항목 | 선택 |
|------|------|
| 파이프라인 | Python (`packages/pipeline`) |
| API | FastAPI (`services/api`) |
| 데모 | Next.js (`apps/web`) |
| 코퍼스 | `document/dobedub` (로컬, gitignore) |
| 벡터 DB | Qdrant (로컬 Docker / 기존 6333) |
| 임베딩 | `BAAI/bge-m3` |
| Re-rank | `BAAI/bge-reranker-v2-m3` |
| LLM | Cursor SDK (`CURSOR_API_KEY`) |

설계 상세: [`docs/superpowers/specs/2026-07-22-claim-level-grounding-guard-design.md`](docs/superpowers/specs/2026-07-22-claim-level-grounding-guard-design.md)

## 레포 구조

```
apps/web/                 Next.js 데모 (Guard ON/OFF, claim 색칠)
services/api/             FastAPI  /health  /ask
packages/pipeline/        ingest · retrieve · rerank · generate · verify
document/dobedub/         RAG 코퍼스 (*.md는 gitignore)
data/eval/                미니 eval set
docker-compose.yml        Qdrant (호스트 6335)
scripts/sync_dobedub_corpus.sh
.env.example              공개 설정 템플릿
```

## 시크릿 / 대외비

- `document/dobedub/*.md` — **커밋 금지** (gitignore)
- `.env` / `.env.local` — **커밋 금지** (`CURSOR_API_KEY` 등)
- `.env.example`만 커밋

```bash
# .env.local 예시
CURSOR_API_KEY=cursor_...
CURSOR_MODEL=composer-2.5
```

## 코퍼스

원본: `~/Documents/dobedub`  
로컬 복사:

```bash
bash scripts/sync_dobedub_corpus.sh
```

Eval: `data/eval/dobedub_eval.jsonl` (`answerable` / `should_refuse`)

## 로컬 실행

Python **3.11+** 필요.

### 1) Qdrant

이미 `localhost:6333`이면 그대로 사용.

없으면:

```bash
docker compose up -d
export QDRANT_URL=http://localhost:6335
```

### 2) 파이프라인

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e "packages/pipeline[dev]" -e "services/api[dev]"

python -m grounding_pipeline ingest
python -m grounding_pipeline retrieve "덥라이트 기술 스택은?" -k 3
python -m grounding_pipeline ask "보고팡 이용자 프론트엔드의 시스템 코드는?" -k 3
python -m grounding_pipeline ask "..." -k 3 --no-guard   # verify OFF
```

첫 ingest / re-rank는 모델 다운로드로 시간이 걸릴 수 있습니다.

### 3) API + 데모 UI

```bash
# 터미널 1
source .venv/bin/activate
uvicorn app.main:app --reload --app-dir services/api --port 8000

# 터미널 2
cd apps/web && npm run dev
```

- Web: http://localhost:3000  
- Health: http://localhost:8000/health  
- Ask: `POST /ask` `{ "question": "...", "guard": true }`

종료: 각 터미널에서 `Ctrl+C`, 가상환경은 `deactivate`.

## Claim 라벨 (데모 색)

| 라벨 | 의미 | Gate |
|------|------|------|
| `supported` | 인용 청크가 주장을 지지 | 유지 |
| `partial` | 관련이나 과장/누락 | 유지 (+경고) |
| `unsupported` | 인용과 내용 불일치 | 제거 |
| `uncited` | 인용 없는 주장 | 제거 |

남는 claim이 없으면 거절: `제공된 문서만으로는 답할 수 없습니다.`

## 진행 상황

- [x] 방향·설계 문서화
- [x] 모노레포 스캐폴드
- [x] dobedub 코퍼스 sync + eval set
- [x] Ingest / Retrieve (BGE-M3 + Qdrant)
- [x] Re-rank (BGE-reranker-v2-m3)
- [x] Cite-forced generate (Cursor SDK)
- [x] Claim verify + refusal gate
- [x] 데모 UI (ON/OFF, claim 색칠)
- [ ] (optional) 검색 품질 개선 · eval 대시보드 · span 단위 인용

## License

MIT (예정)
