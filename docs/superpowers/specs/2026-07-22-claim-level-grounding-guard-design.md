# Claim-level Grounding Guard — Design Spec

**Date:** 2026-07-22  
**Status:** Approved direction (MVP not yet implemented)  
**Repo:** `rag-hallucination-control`

## 1. Problem

RAG alone does not stop hallucinations. Models still invent facts when retrieval is weak, and they can attach plausible-looking citations that do not support the claim. Portfolio demos that are “chat over PDFs” do not show control.

## 2. Product thesis

Ship a **claim-level grounding guard**: every sentence/claim in the answer must map to a source span and pass a faithfulness check. Unsupported or uncited claims are stripped, rewritten, or refused. The demo proves trust by making provenance visible.

## 3. Goals / non-goals

### Goals (MVP)

- Korean document corpus Q&A with citation-forced generation
- Claim decompose → verify → `supported | partial | unsupported | uncited`
- Refusal when nothing remains grounded
- Demo UI: control ON/OFF compare, claim coloring, source span highlight, evidence report
- Small eval set (20–30 questions) with measurable faithfulness / unsupported / refusal rates

### Non-goals (MVP)

- Full agentic rewrite-retry loop (optional Phase 2)
- Hybrid BM25 + vector production retrieval tuning
- Auth, multi-tenant, large-scale ingestion
- Training / fine-tuning models

## 4. Stack (demo + pipeline)

| Layer | Choice | Role |
|-------|--------|------|
| Pipeline | Python | retrieve → generate → claim split → verify → filter/refuse |
| API | FastAPI | thin HTTP boundary for the demo |
| Demo | Next.js | ON/OFF UI, claim colors, span highlight, evidence report |
| Store | Chroma or FAISS (start simple) | vector retrieval |
| LLM | OpenAI / Anthropic / Gemini (one provider first) | generate + judge |

Monorepo layout (planned):

```
/
├── apps/web/          # Next.js demo
├── services/api/      # FastAPI
├── packages/pipeline/ # core grounding logic + evals
├── data/              # sample Korean corpus + eval set
└── docs/
```

## 5. Pipeline

```
query
  → retrieve(k)
  → generate with mandatory per-sentence citations [n]
  → decompose answer into atomic claims
  → for each claim: verify against cited span(s)
       supported | partial | unsupported | uncited
  → filter / rewrite / refuse
  → return answer + evidence report
```

### Verification labels

| Label | Meaning | Default action |
|-------|---------|----------------|
| `supported` | Cited span entails the claim | keep |
| `partial` | Related but overstated / incomplete | keep with warning or soften |
| `unsupported` | Citation present but does not support claim | drop or block |
| `uncited` | Claim has no citation | drop or block |

Control OFF path: same retrieve + generate, skip verify gate (for A/B demo).

## 6. Demo UX (portfolio face)

1. Upload / select Korean docs
2. Ask a question
3. Toggle **Grounding Guard ON/OFF**
4. Side-by-side or sequential compare
5. Click a claim → highlight supporting span in source
6. Evidence report table: claim ↔ span ↔ verdict

## 7. Eval (minimum bar)

- 20–30 Korean questions: answerable vs should-refuse
- Metrics: faithfulness (or supported rate), unsupported rate, refusal precision/recall
- Script under `packages/pipeline` runnable in CI later

## 8. Phase 2 (optional)

Self-correcting loop: on verify fail → query rewrite → re-retrieve → regenerate (max N), then refuse. Extends this design; does not replace claim-level gating.

## 9. Success criteria for portfolio

- Viewer understands in 30s: “unsupported claims cannot leave the system”
- Clear before/after with control toggle
- At least one quantitative before/after number on the README
- Code structure separates **guard logic** from **chat UI**
