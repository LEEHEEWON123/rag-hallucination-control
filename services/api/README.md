# grounding-api

Next.js 데모가 호출하는 **얇은 FastAPI 레이어**.

비즈니스 로직은 `packages/pipeline`에 두고, 여기는 HTTP만 담당한다.

## 실행 (로컬)

repo root에서:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e packages/pipeline
pip install -e "services/api[dev]"
uvicorn app.main:app --reload --app-dir services/api --port 8000
```

헬스체크: `GET http://localhost:8000/health`
