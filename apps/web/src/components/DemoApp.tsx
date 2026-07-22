"use client";

import { FormEvent, useMemo, useState } from "react";

type Claim = {
  claim: string;
  citations: number[];
  label: "supported" | "partial" | "unsupported" | "uncited" | string;
  reason?: string;
  raw?: string;
};

type Chunk = {
  n: number;
  doc_id?: string;
  chunk_id?: string;
  text?: string;
  score?: number;
};

type AskResult = {
  question: string;
  answer: string;
  draft_answer?: string | null;
  refused: boolean;
  guard: boolean;
  claims: Claim[];
  chunks: Chunk[];
  model?: string | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const LABEL_STYLE: Record<string, string> = {
  supported: "bg-emerald-100 text-emerald-900 ring-emerald-300",
  partial: "bg-amber-100 text-amber-950 ring-amber-300",
  unsupported: "bg-rose-100 text-rose-900 ring-rose-300",
  uncited: "bg-rose-100 text-rose-900 ring-rose-300",
};

function labelClass(label: string) {
  return LABEL_STYLE[label] ?? "bg-zinc-100 text-zinc-800 ring-zinc-300";
}

export function DemoApp() {
  const [question, setQuestion] = useState(
    "보고팡 이용자 프론트엔드의 시스템 코드는?",
  );
  const [guard, setGuard] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResult | null>(null);

  const claimSummary = useMemo(() => {
    if (!result?.claims?.length) return null;
    const counts: Record<string, number> = {};
    for (const c of result.claims) {
      counts[c.label] = (counts[c.label] ?? 0) + 1;
    }
    return counts;
  }, [result]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          guard,
          top_k: 5,
          candidate_k: 20,
          use_rerank: true,
        }),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `HTTP ${response.status}`);
      }
      const data = (await response.json()) as AskResult;
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : "요청 실패");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-10 px-6 py-12 md:py-16">
      <header className="space-y-3">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-800/80">
          RAG Hallucination Control
        </p>
        <h1 className="font-[family-name:var(--font-display)] text-4xl leading-tight tracking-tight text-zinc-900 md:text-5xl">
          Claim-level Grounding Guard
        </h1>
        <p className="max-w-2xl text-base leading-7 text-zinc-600">
          retrieve → re-rank → cite-forced generate → claim verify.
          통제 ON이면 근거 없는 문장을 걸러내고, OFF면 초안을 그대로 보여줍니다.
        </p>
      </header>

      <form onSubmit={onSubmit} className="space-y-5 border-y border-zinc-200 py-6">
        <label className="block space-y-2">
          <span className="text-sm font-medium text-zinc-800">질문</span>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={3}
            className="w-full resize-y rounded-md border border-zinc-300 bg-white px-3 py-2 text-base text-zinc-900 outline-none ring-teal-700/30 focus:ring-2"
            placeholder="문서 기반으로 물어볼 내용을 입력하세요"
            required
          />
        </label>

        <div className="flex flex-wrap items-center justify-between gap-4">
          <label className="inline-flex items-center gap-3 text-sm text-zinc-800">
            <span className="font-medium">Grounding Guard</span>
            <button
              type="button"
              role="switch"
              aria-checked={guard}
              onClick={() => setGuard((v) => !v)}
              className={`relative h-7 w-12 rounded-full transition-colors ${
                guard ? "bg-teal-700" : "bg-zinc-300"
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 h-6 w-6 rounded-full bg-white transition-transform ${
                  guard ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>
            <span className="font-mono text-xs tracking-wide text-zinc-500">
              {guard ? "ON" : "OFF"}
            </span>
          </label>

          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-md bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white transition enabled:hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "검증 중… (수십 초 걸릴 수 있음)" : "질문하기"}
          </button>
        </div>
      </form>

      {error ? (
        <p className="rounded-md bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</p>
      ) : null}

      {result ? (
        <section className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                <span className="rounded bg-zinc-100 px-2 py-1 font-mono">
                  guard={result.guard ? "ON" : "OFF"}
                </span>
                <span className="rounded bg-zinc-100 px-2 py-1 font-mono">
                  refused={String(result.refused)}
                </span>
                {result.model ? (
                  <span className="rounded bg-zinc-100 px-2 py-1 font-mono">
                    model={result.model}
                  </span>
                ) : null}
              </div>
              <h2 className="text-lg font-semibold text-zinc-900">최종 답변</h2>
              <p className="whitespace-pre-wrap text-base leading-8 text-zinc-800">
                {result.answer}
              </p>
            </div>

            {result.draft_answer &&
            result.draft_answer !== result.answer &&
            result.guard ? (
              <div className="space-y-2 border-t border-zinc-200 pt-5">
                <h3 className="text-sm font-semibold text-zinc-700">초안 (gate 전)</h3>
                <p className="whitespace-pre-wrap text-sm leading-7 text-zinc-500">
                  {result.draft_answer}
                </p>
              </div>
            ) : null}

            <div className="space-y-3 border-t border-zinc-200 pt-5">
              <div className="flex flex-wrap items-end justify-between gap-2">
                <h3 className="text-lg font-semibold text-zinc-900">Claims</h3>
                {claimSummary ? (
                  <p className="font-mono text-xs text-zinc-500">
                    {Object.entries(claimSummary)
                      .map(([k, v]) => `${k}:${v}`)
                      .join(" · ")}
                  </p>
                ) : null}
              </div>

              {!result.claims?.length ? (
                <p className="text-sm text-zinc-500">
                  {result.guard
                    ? "검증된 claim이 없습니다."
                    : "Guard OFF — claim 판정을 건너뛰었습니다."}
                </p>
              ) : (
                <ul className="space-y-3">
                  {result.claims.map((claim, index) => (
                    <li
                      key={`${claim.claim}-${index}`}
                      className={`rounded-md px-3 py-3 text-sm ring-1 ${labelClass(claim.label)}`}
                    >
                      <div className="mb-1 flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs uppercase tracking-wide">
                          {claim.label}
                        </span>
                        <span className="font-mono text-xs opacity-70">
                          citations=
                          {claim.citations?.length
                            ? `[${claim.citations.join(",")}]`
                            : "[]"}
                        </span>
                      </div>
                      <p className="leading-6">{claim.claim}</p>
                      {claim.reason ? (
                        <p className="mt-2 text-xs leading-5 opacity-80">{claim.reason}</p>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <aside className="space-y-3 lg:border-l lg:border-zinc-200 lg:pl-8">
            <h3 className="text-lg font-semibold text-zinc-900">Cited chunks</h3>
            <ul className="space-y-4">
              {result.chunks.map((chunk) => (
                <li key={chunk.n} className="space-y-1">
                  <p className="font-mono text-xs text-teal-800">
                    [{chunk.n}] {chunk.doc_id}
                  </p>
                  <p className="text-sm leading-6 text-zinc-600">
                    {(chunk.text ?? "").slice(0, 280)}
                    {(chunk.text?.length ?? 0) > 280 ? "…" : ""}
                  </p>
                </li>
              ))}
            </ul>
          </aside>
        </section>
      ) : null}
    </main>
  );
}
