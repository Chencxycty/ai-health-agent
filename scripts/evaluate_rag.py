import json
from pathlib import Path

from health_agent.rag.factory import (
    build_rag_service,
)

EVAL_FILE = Path("data/eval/rag_golden.json")


def main() -> None:
    with EVAL_FILE.open(
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    service = build_rag_service()

    for case in cases:
        result = service.answer(case["query"])

        retrieved_pages = {citation.page for citation in result.citations}

        expected_pages = set(case["expected_pages"])

        retrieval_hit = bool(retrieved_pages & expected_pages)

        if not expected_pages:
            retrieval_hit = True

        keyword_hits = [
            keyword for keyword in case["keywords"] if keyword in result.answer
        ]

        print("=" * 80)

        print(f"ID: {case['id']}")

        print(f"Query: {case['query']}")

        print(f"Retrieval hit: {retrieval_hit}")

        print(f"Keyword hits: {keyword_hits}")

        print(
            "Pages:",
            sorted(retrieved_pages),
        )

        print("Answer:")

        print(result.answer)

        print(f"Latency: {result.total_latency_ms:.2f} ms")

        print(f"Tokens: {result.total_tokens}")


if __name__ == "__main__":
    main()
