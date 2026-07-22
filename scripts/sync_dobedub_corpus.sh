#!/usr/bin/env bash
# Sync curated DuBeDub docs into document/dobedub (local only, gitignored).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${DOBEDUB_SRC:-$HOME/Documents/dobedub}"
DEST="$ROOT/document/dobedub"

if [[ ! -d "$SRC" ]]; then
  echo "Source not found: $SRC"
  echo "Set DOBEDUB_SRC to your dobedub workspace path."
  exit 1
fi

mkdir -p "$DEST"

copy() {
  local from="$1"
  local to="$2"
  if [[ -f "$from" ]]; then
    cp "$from" "$DEST/$to"
    echo "copied $to"
  else
    echo "skip (missing): $from"
  fi
}

copy "$SRC/dobedub_last/BP_FE_OPS_v0.9_20260709.md" "bp-fe-ops.md"
copy "$SRC/dobedub_last/BP_FE_ARCH_v 0.9_20260709.md" "bp-fe-arch.md"
copy "$SRC/dobedub_last/PM_FE_OPS_v0.9_20260709.md" "pm-fe-ops.md"
copy "$SRC/dobedub_last/PT_FE_OPS_v0.9_20260709.md" "pt-fe-ops.md"
copy "$SRC/dobedub_last/두비덥_05_시스템_덥라이트_운영문서_프론트엔드.md" "dr-fe-ops.md"
copy "$SRC/dobedub_last/두비덥_05_시스템_보고팡_운영문서_프론트엔드.md" "bp-fe-ops-system.md"
copy "$SRC/dobedub_last/두비덥_03_CICD_구성도_덥라이트_프론트엔드.md" "dr-cicd.md"
copy "$SRC/dobedub_last/두비덥_03_CICD_구성도_보고팡_프론트엔드.md" "bp-cicd.md"
copy "$SRC/dubright_front/PROJECT_GUIDE.md" "dr-project-guide.md"
copy "$SRC/dubright_backend/DB_SCHEMA.md" "dr-db-schema.md"

# Redact common secret-looking values in local copies
perl -i -pe '
  s/(VITE_ENCRYPTION_KEY\s*\|\s*)[A-Za-z0-9+/=_-]{16,}/$1REDACTED/gi;
  s/(VITE_SENDBIRD_APP_ID\s*\|\s*)[A-F0-9-]{20,}/$1REDACTED/gi;
  s/(VITE_UMAMI_WEBSITE_ID\s*\|\s*)[a-f0-9-]{20,}/$1REDACTED/gi;
' "$DEST"/*.md

# Keep README
cat > "$DEST/README.md" <<'EOF'
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

Eval 질문은 `data/eval/dobedub_eval.jsonl`을 본다.
EOF

echo "Done. Corpus at $DEST"
ls -1 "$DEST"
