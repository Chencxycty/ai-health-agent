from health_agent.rag.factory import (
    build_rag_service,
)


def main() -> None:
    service = build_rag_service()

    query = "高血压患者应该如何进行家庭血压监测？"

    result = service.answer(query=query)

    print()
    print("QUESTION")
    print(query)

    print()
    print("ANSWER")
    print(result.answer)

    print()
    print("SOURCES")

    for citation in result.citations:
        print(
            f"[Source "
            f"{citation.source_id}] "
            f"{citation.title} "
            f"page={citation.page} "
            f"chunk={citation.chunk_id}"
        )

    print()
    print(
        "retrieval_ms:",
        round(
            result.retrieval_latency_ms,
            2,
        ),
    )

    print(
        "generation_ms:",
        round(
            result.generation_latency_ms,
            2,
        ),
    )

    print(
        "total_ms:",
        round(
            result.total_latency_ms,
            2,
        ),
    )

    print(
        "tokens:",
        result.total_tokens,
    )


if __name__ == "__main__":
    main()
