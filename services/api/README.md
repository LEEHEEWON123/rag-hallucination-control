# grounding-api

Next.js 데모가 호출하는 **얇은 FastAPI 레이어**.

- `GET /health`
- `POST /ask` — retrieve → generate → (optional) claim verify

## 실행

repo root:

```bash
source .venv/bin/activate
pip install -e packages/pipeline -e "services/api[dev]"
uvicorn app.main:app --reload --app-dir services/api --port 8000
```

Ask 예:

```bash
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"보고팡 이용자 프론트엔드의 시스템 코드는?","guard":true,"top_k":3}'
```
