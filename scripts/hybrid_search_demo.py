from health_agent.rag.factory import (
    build_hybrid_retriever,
)


def main() -> None:
    # 构建混合检索器
    retriever = build_hybrid_retriever(use_reranker=True)

    query = "高血压患者如何进行家庭血压监测？"

    # 使用混合检索器进行查询
    results = retriever.search(
        query=query,
        top_k=5,
    )

    print(f"\nQuery: {query}\n")

    # 打印检索结果
    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"[{index}] score={result.score:.4f} page={result.chunk.page}")

        print(result.chunk.content[:400])

        print("-" * 80)


if __name__ == "__main__":
    main()
