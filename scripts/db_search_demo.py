from health_agent.rag.vector_retriever import (
    VectorRetriever,
)


def main() -> None:
    retriever = VectorRetriever()

    query = "高血压患者家庭血压监测有哪些要求？"

    results = retriever.search(
        query=query,
        top_k=5,
    )

    print()
    print(f"Query: {query}")
    print()

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"[{index}] score={result.score:.4f} page={result.chunk.page}")

        print(result.chunk.content[:300])

        print("-" * 80)


if __name__ == "__main__":
    main()
