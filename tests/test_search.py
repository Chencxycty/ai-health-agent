import numpy as np
import pytest

from health_agent.rag.schemas import DocumentChunk
from health_agent.rag.search import cosine_search


def make_chunk(
    chunk_id: str,
    page: int,
    content: str,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        title="test-document",
        source="test.pdf",
        page=page,
        chunk_index=page - 1,
        content=content,
    )


def test_cosine_search_returns_most_similar_chunk() -> None:
    chunks = [
        make_chunk(
            chunk_id="chunk-1",
            page=1,
            content="高血压患者需要定期监测血压。",
        ),
        make_chunk(
            chunk_id="chunk-2",
            page=2,
            content="糖尿病患者需要关注血糖变化。",
        ),
        make_chunk(
            chunk_id="chunk-3",
            page=3,
            content="健康饮食有助于慢病管理。",
        ),
    ]

    document_embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float32,
    )

    query_embedding = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    results = cosine_search(
        query_embedding=query_embedding,
        document_embeddings=document_embeddings,
        chunks=chunks,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk.chunk_id == "chunk-1"
    assert results[0].score == pytest.approx(1.0)


def test_cosine_search_orders_results_by_score() -> None:
    chunks = [
        make_chunk("chunk-1", 1, "A"),
        make_chunk("chunk-2", 2, "B"),
        make_chunk("chunk-3", 3, "C"),
    ]

    document_embeddings = np.array(
        [
            [1.0, 0.0],
            [0.8, 0.6],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )

    query_embedding = np.array(
        [1.0, 0.0],
        dtype=np.float32,
    )

    results = cosine_search(
        query_embedding=query_embedding,
        document_embeddings=document_embeddings,
        chunks=chunks,
        top_k=3,
    )

    assert [result.chunk.chunk_id for result in results] == [
        "chunk-1",
        "chunk-2",
        "chunk-3",
    ]

    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score


def test_cosine_search_respects_top_k() -> None:
    chunks = [
        make_chunk("chunk-1", 1, "A"),
        make_chunk("chunk-2", 2, "B"),
        make_chunk("chunk-3", 3, "C"),
    ]

    document_embeddings = np.array(
        [
            [1.0, 0.0],
            [0.8, 0.6],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )

    query_embedding = np.array(
        [1.0, 0.0],
        dtype=np.float32,
    )

    results = cosine_search(
        query_embedding=query_embedding,
        document_embeddings=document_embeddings,
        chunks=chunks,
        top_k=2,
    )

    assert len(results) == 2


def test_cosine_search_rejects_length_mismatch() -> None:
    chunks = [
        make_chunk("chunk-1", 1, "A"),
        make_chunk("chunk-2", 2, "B"),
    ]

    document_embeddings = np.array(
        [
            [1.0, 0.0],
        ],
        dtype=np.float32,
    )

    query_embedding = np.array(
        [1.0, 0.0],
        dtype=np.float32,
    )

    with pytest.raises(
        ValueError,
        match="same length",
    ):
        cosine_search(
            query_embedding=query_embedding,
            document_embeddings=document_embeddings,
            chunks=chunks,
            top_k=1,
        )
