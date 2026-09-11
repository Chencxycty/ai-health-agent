import json
from pathlib import Path

from health_agent.rag.factory import (
    build_hybrid_retriever,
)

EVAL_FILE = Path("data/eval/retrieval_golden.json")


def hit_at_k(
    retrieved_pages: list[int],
    relevant_pages: set[int],
    k: int,
) -> float:
    """计算 Hit@k 指标。"""
    top_pages = set(retrieved_pages[:k])

    return float(bool(top_pages & relevant_pages))


def reciprocal_rank(
    retrieved_pages: list[int],
    relevant_pages: set[int],
) -> float:
    """计算 MRR（Mean Reciprocal Rank）指标。"""
    for rank, page in enumerate(
        retrieved_pages,
        start=1,
    ):
        if page in relevant_pages:
            return 1.0 / rank

    return 0.0


def main() -> None:
    with EVAL_FILE.open(
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    # 构建混合检索器
    retriever = build_hybrid_retriever(use_reranker=True)

    totals = {
        "hit1": 0.0,
        "hit3": 0.0,
        "hit5": 0.0,
        "mrr": 0.0,
    }

    # 遍历每个查询案例，计算指标
    for case in cases:
        query = case["query"]

        relevant_pages = set(case["relevant_pages"])

        results = retriever.search(
            query=query,
            top_k=10,
        )

        pages = [result.chunk.page for result in results]

        # 计算 Hit@1, Hit@3, Hit@5 和 MRR 指标
        h1 = hit_at_k(
            pages,
            relevant_pages,
            1,
        )

        h3 = hit_at_k(
            pages,
            relevant_pages,
            3,
        )

        h5 = hit_at_k(
            pages,
            relevant_pages,
            5,
        )

        rr = reciprocal_rank(
            pages,
            relevant_pages,
        )

        totals["hit1"] += h1
        totals["hit3"] += h3
        totals["hit5"] += h5
        totals["mrr"] += rr

        print(f"{case['id']}: H@1={h1:.0f} H@3={h3:.0f} H@5={h5:.0f} RR={rr:.3f}")

    count = len(cases)

    print()
    print(f"Hit@1: {totals['hit1'] / count:.3f}")

    print(f"Hit@3: {totals['hit3'] / count:.3f}")

    print(f"Hit@5: {totals['hit5'] / count:.3f}")

    print(f"MRR: {totals['mrr'] / count:.3f}")


if __name__ == "__main__":
    main()
