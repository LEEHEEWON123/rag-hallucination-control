export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col justify-center gap-4 px-6 py-16">
      <p className="text-sm tracking-wide text-zinc-500">RAG Hallucination Control</p>
      <h1 className="text-3xl font-semibold tracking-tight text-zinc-900">
        Claim-level Grounding Guard
      </h1>
      <p className="text-base leading-7 text-zinc-600">
        데모 UI 스캐폴드입니다. 다음 단계에서 API health를 연결하고, 통제 ON/OFF
        비교 화면을 붙입니다.
      </p>
      <code className="rounded bg-zinc-100 px-3 py-2 text-sm text-zinc-800">
        GET http://localhost:8000/health
      </code>
    </main>
  );
}
