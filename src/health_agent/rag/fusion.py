from collections import defaultdict

from health_agent.rag.schemas import (
    SearchResult,
)


def reciprocal_rank_fusion(
    result_lists: list[list[SearchResult]],
    k: int = 60,
    top_k: int = 20,
) -> list[SearchResult]:
    """使用RRR（Reciprocal Rank Fusion）算法融合多个检索结果列表。"""
    if k <= 0:
        raise ValueError("k must be greater than 0.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0.")

    scores: dict[str, float] = defaultdict(float)
    chunks = {}

    for results in result_lists:
        for rank, result in enumerate(
            results,
            start=1,
        ):
            chunk_id = result.chunk.chunk_id

            # 计算RRR分数
            scores[chunk_id] += 1.0 / (k + rank)

            chunks[chunk_id] = result.chunk

    ranked_ids = sorted(
        scores,
        key=lambda chunk_id: scores[chunk_id],
        reverse=True,
    )[:top_k]

    return [
        SearchResult(
            chunk=chunks[chunk_id],
            score=scores[chunk_id],
        )
        for chunk_id in ranked_ids
    ]
