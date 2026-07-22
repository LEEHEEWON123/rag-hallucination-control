# data/eval

미니 eval set. 코퍼스 `document/dobedub` 기준.

## 파일

- `dobedub_eval.jsonl` — 질문 + 기대 행동

## 스키마

| 필드 | 설명 |
|------|------|
| `id` | 질문 ID |
| `question` | 한국어 질문 |
| `expect` | `answerable` \| `should_refuse` |
| `gold_doc_ids` | 근거가 있을 법한 문서 stem 목록 |
| `notes` | 사람이 보는 힌트 (채점용, 모델 입력 아님) |

파이프라인 MVP 이후 여기서 faithfulness / refusal 수치를 뽑는다.
