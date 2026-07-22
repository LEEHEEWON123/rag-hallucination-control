# document/dobedub

로컬 RAG 코퍼스 루트. **대외비 운영문서를 여기로 복사해서 사용**한다.

## 중요

- 이 폴더의 `*.md`는 **Git에 커밋하지 않는다** (`.gitignore`).
- 원본 위치: `~/Documents/dobedub/` (운영문서·프로젝트 가이드 등).
- 시크릿(암호화 키, SendBird ID 등)이 문서에 있으면 sync 시 레드액트한다.

## 동기화

repo root에서:

```bash
bash scripts/sync_dobedub_corpus.sh
```

## 현재 포함 문서 (예시)

| 파일 | 출처 |
|------|------|
| `bp-fe-ops.md` | 보고팡 FE 운영 |
| `bp-fe-arch.md` | 보고팡 FE 아키텍처 |
| `pm-fe-ops.md` | 픽미툰 FE 운영 |
| `pt-fe-ops.md` | 푸딩툰 FE 운영 |
| `dr-fe-ops.md` | 덥라이트 FE 운영 |
| `dr-project-guide.md` | 덥라이트 프로젝트 가이드 |
| `dr-cicd.md` / `bp-cicd.md` | CI/CD 구성 |
| `dr-db-schema.md` | 덥라이트 DB 스키마 |

Eval 질문은 `data/eval/dobedub_eval.jsonl`을 본다.
