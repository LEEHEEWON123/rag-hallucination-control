"""CLI: ingest / retrieve / ask (generate + verify gate)."""

from __future__ import annotations

import argparse
import json

from grounding_pipeline.env import load_env
from grounding_pipeline.generate import ask
from grounding_pipeline.ingest import ingest_corpus
from grounding_pipeline.retrieve import retrieve


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="Grounding pipeline — ingest / retrieve / ask")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Chunk + embed corpus into Qdrant")
    p_ingest.add_argument(
        "--no-recreate",
        action="store_true",
        help="Do not delete existing collection before upsert",
    )

    p_retrieve = sub.add_parser("retrieve", help="Dense retrieve + optional cross-encoder re-rank")
    p_retrieve.add_argument("query", type=str)
    p_retrieve.add_argument("-k", "--top-k", type=int, default=None, help="Final chunks after re-rank")
    p_retrieve.add_argument(
        "-c",
        "--candidate-k",
        type=int,
        default=None,
        help="Candidates from Qdrant before re-rank",
    )
    p_retrieve.add_argument(
        "--no-rerank",
        action="store_true",
        help="Skip re-rank (vector scores only)",
    )

    p_ask = sub.add_parser("ask", help="Retrieve → generate → claim verify gate")
    p_ask.add_argument("query", type=str)
    p_ask.add_argument("-k", "--top-k", type=int, default=None)
    p_ask.add_argument("-c", "--candidate-k", type=int, default=None)
    p_ask.add_argument("--no-rerank", action="store_true")
    p_ask.add_argument("--no-guard", action="store_true", help="Skip claim verify (control OFF)")
    p_ask.add_argument("--json", action="store_true", help="Print full JSON result")

    args = parser.parse_args()

    if args.command == "ingest":
        result = ingest_corpus(recreate=not args.no_recreate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == "retrieve":
        hits = retrieve(
            args.query,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_rerank=not args.no_rerank,
        )
        for i, hit in enumerate(hits, 1):
            preview = (hit.get("text") or "").replace("\n", " ")[:180]
            vec = hit.get("vector_score")
            rr = hit.get("rerank_score")
            score_bits = [f"score={hit['score']:.4f}"]
            if vec is not None:
                score_bits.append(f"vector={float(vec):.4f}")
            if rr is not None:
                score_bits.append(f"rerank={float(rr):.4f}")
            print(f"[{i}] {' '.join(score_bits)} doc={hit['doc_id']} chunk={hit['chunk_id']}")
            print(f"    {preview}")
            print()
        return

    if args.command == "ask":
        result = ask(
            args.query,
            top_k=args.top_k,
            candidate_k=args.candidate_k,
            use_rerank=not args.no_rerank,
            guard=not args.no_guard,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        print("=== FINAL ANSWER ===")
        print(result["answer"])
        if result.get("draft_answer") and result["draft_answer"] != result["answer"]:
            print()
            print("=== DRAFT (before gate) ===")
            print(result["draft_answer"])
        print()
        print(f"guard={'ON' if result.get('guard') else 'OFF'} refused={result.get('refused')}")
        if result.get("claims"):
            print()
            print("=== CLAIMS ===")
            for claim in result["claims"]:
                print(
                    f"- [{claim['label']}] citations={claim['citations']} "
                    f":: {claim['claim']}"
                )
                if claim.get("reason"):
                    print(f"  reason: {claim['reason']}")
        print()
        print("=== CHUNKS ===")
        for chunk in result["chunks"]:
            preview = (chunk.get("text") or "").replace("\n", " ")[:140]
            print(f"[{chunk['n']}] doc={chunk['doc_id']} chunk={chunk['chunk_id']}")
            print(f"    {preview}")
            print()
        return


if __name__ == "__main__":
    main()
