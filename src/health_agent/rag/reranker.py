from sentence_transformers import CrossEncoder

from health_agent.rag.schemas import (
    SearchResult,
)


class Reranker:
    def __init__(
        self,
        model_name: str,
    ) -> None:
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """根据查询对检索结果进行重排序（rerank）。"""
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        if not results:
            return []

        pairs = [
            (
                query,
                result.chunk.content,
            )
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = [
            SearchResult(
                chunk=result.chunk,
                score=float(score),
            )
            for result, score in zip(
                results,
                scores,
                strict=True,
            )
        ]

        return sorted(
            reranked,
            key=lambda item: item.score,
            reverse=True,
        )[:top_k]
