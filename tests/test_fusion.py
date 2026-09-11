from health_agent.rag.fusion import (
    reciprocal_rank_fusion,
)
from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


def make_result(
    chunk_id: str,
    score: float,
) -> SearchResult:
    chunk = DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc",
        title="test",
        source="test",
        page=1,
        chunk_index=0,
        content=chunk_id,
    )

    return SearchResult(
        chunk=chunk,
        score=score,
    )


def test_rrf_rewards_results_from_multiple_lists() -> None:
    vector_results = [
        make_result("A", 0.9),
        make_result("B", 0.8),
        make_result("C", 0.7),
    ]

    bm25_results = [
        make_result("B", 10.0),
        make_result("A", 8.0),
        make_result("D", 7.0),
    ]

    results = reciprocal_rank_fusion(
        [
            vector_results,
            bm25_results,
        ],
        top_k=4,
    )

    ids = [result.chunk.chunk_id for result in results]

    assert ids[0] in {
        "A",
        "B",
    }

    assert ids[1] in {
        "A",
        "B",
    }
