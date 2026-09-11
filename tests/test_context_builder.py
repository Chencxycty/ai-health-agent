from health_agent.rag.context_builder import (
    build_context,
)
from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


def test_build_context_contains_metadata() -> None:
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        title="高血压指南",
        source="test.pdf",
        page=12,
        chunk_index=0,
        content="家庭血压监测相关内容。",
    )

    context = build_context(
        [
            SearchResult(
                chunk=chunk,
                score=0.9,
            )
        ]
    )

    assert "[Source 1]" in context
    assert "高血压指南" in context
    assert "Page: 12" in context
    assert "chunk-1" in context
    assert "家庭血压监测" in context
