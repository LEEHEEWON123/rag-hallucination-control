# RAG Hallucination Control

포트폴리오 프로젝트: RAG 답변을 위한 **Claim-level Grounding Guard**.

RAG는 문서를 검색할 뿐, 할루시에이션을 막아주지는 않습니다. 이 프로젝트는 답변의 각 claim이 인용된 출처 span으로 뒷받침되는지 검사하고, 근거 없거나 잘못된 인용은 걸러내거나 거절합니다. 데모 UI로 “왜 믿을 수 있는지”를 보여줍니다.

## 방향

| 항목 | 선택 |
|------|------|
| 핵심 아이디어 | Claim 단위 citation + faithfulness gate + refusal |
| 스택 | Python 파이프라인 + FastAPI + Next.js 데모 |
| 코퍼스 | 한국어 문서 (샘플셋 TBD) |
| 차별점 | 통제 ON/OFF 비교 + 증거 리포트 UI |

설계 상세: [`docs/superpowers/specs/2026-07-22-claim-level-grounding-guard-design.md`](docs/superpowers/specs/2026-07-22-claim-level-grounding-guard-design.md)

## 레포 구조

```
apps/web/              Next.js 데모
services/api/          FastAPI (얇은 HTTP)
packages/pipeline/     grounding 핵심 로직
document/dobedub/      RAG 코퍼스 (로컬, gitignore)
data/eval/             미니 eval set
data/corpus_manifest.json
docs/                  설계 문서
scripts/sync_dobedub_corpus.sh
```

## 코퍼스 (dobedub)

원본: `~/Documents/dobedub` 운영문서·가이드.  
로컬 복사: `document/dobedub/` (**대외비 → Git 커밋 금지**).

```bash
bash scripts/sync_dobedub_corpus.sh
```

Eval: `data/eval/dobedub_eval.jsonl` (answerable / should_refuse)
## 로컬 실행

Python 3.11+ 필요.

```bash
# API
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e packages/pipeline -e "services/api[dev]"
uvicorn app.main:app --reload --app-dir services/api --port 8000

# Web (다른 터미널)
cd apps/web && npm run dev
```

- API health: http://localhost:8000/health
- Web: http://localhost:3000

## 파이프라인 (목표)

```
retrieve → cite-forced generate → claim split → verify
  → supported | partial | unsupported | uncited
  → filter / refuse → evidence report
```

## 진행 상황

- [x] 방향·설계 문서화
- [x] 모노레포 스캐폴드 (`apps/web`, `services/api`, `packages/pipeline`)
- [x] 한국어 샘플 코퍼스 + 미니 eval set (`document/dobedub` + `data/eval`)
- [ ] Grounding 파이프라인 MVP
- [ ] 데모 UI (ON/OFF, claim 색칠, span 하이라이트)

## License

MIT (예정)
