import pytest

from health_agent.rag.chunker import chunk_page
from health_agent.rag.schemas import PageDocument


def test_chunk_page() -> None:
    page = PageDocument(
        document_id="doc-1",
        title="test",
        source="test.pdf",
        page=1,
        content="A" * 1000,
    )

    chunks = chunk_page(
        page=page,
        chunk_size=400,
        overlap=100,
    )

    assert len(chunks) > 1
    assert chunks[0].page == 1
    assert chunks[0].document_id == "doc-1"


def test_chunk_page_rejects_large_overlap() -> None:
    page = PageDocument(
        document_id="doc-1",
        title="test",
        source="test.pdf",
        page=1,
        content="hello",
    )

    with pytest.raises(ValueError):
        chunk_page(
            page=page,
            chunk_size=100,
            overlap=100,
        )
