from health_agent.rag.bm25_retriever import (
    BM25Retriever,
)
from health_agent.rag.schemas import DocumentChunk


def make_chunk(
    chunk_id: str,
    content: str,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc",
        title="test",
        source="test.pdf",
        page=1,
        chunk_index=0,
        content=content,
    )


def test_bm25_returns_relevant_chunk() -> None:
    chunks = [
        make_chunk(
            "chunk-1",
            "高血压患者需要进行家庭血压监测。",
        ),
        make_chunk(
            "chunk-2",
            "糖尿病患者需要监测血糖。",
        ),
        make_chunk(
            "chunk-3",
            "建议保持规律运动。",
        ),
    ]

    retriever = BM25Retriever(chunks)

    results = retriever.search(
        "家庭血压监测",
        top_k=1,
    )

    assert len(results) == 1

    assert results[0].chunk.chunk_id == "chunk-1"
