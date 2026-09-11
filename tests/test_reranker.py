import numpy as np

from health_agent.rag.reranker import (
    Reranker,
)
from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


class FakeCrossEncoder:
    def predict(
        self,
        pairs,
    ):
        return np.array([0.2, 0.9, 0.5])


def make_result(
    chunk_id: str,
) -> SearchResult:
    return SearchResult(
        chunk=DocumentChunk(
            chunk_id=chunk_id,
            document_id="doc",
            title="test",
            source="test",
            page=1,
            chunk_index=0,
            content=chunk_id,
        ),
        score=0.0,
    )


def test_reranker_orders_by_model_score() -> None:
    reranker = Reranker.__new__(Reranker)

    reranker.model = FakeCrossEncoder()

    results = [
        make_result("A"),
        make_result("B"),
        make_result("C"),
    ]

    reranked = reranker.rerank(
        query="test",
        results=results,
        top_k=3,
    )

    assert [result.chunk.chunk_id for result in reranked] == [
        "B",
        "C",
        "A",
    ]
