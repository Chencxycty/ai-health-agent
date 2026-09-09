from uuid import uuid4

from health_agent.rag.schemas import (
    DocumentChunk,
    PageDocument,
)


def chunk_page(
    page: PageDocument,
    chunk_size: int = 700,  # Chunk size 是一个需要实验的超参数
    overlap: int = 120,
) -> list[DocumentChunk]:
    """将PageDocument对象的内容分割为多个DocumentChunk对象。"""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0:
        raise ValueError("overlap must be non-negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    text = page.content

    chunks: list[DocumentChunk] = []

    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text),
        )

        content = text[start:end].strip()

        if content:
            chunks.append(
                DocumentChunk(
                    chunk_id=str(uuid4()),
                    document_id=page.document_id,
                    title=page.title,
                    source=page.source,
                    page=page.page,
                    chunk_index=chunk_index,
                    content=content,
                )
            )

            chunk_index += 1

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def chunk_document(
    pages: list[PageDocument],
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[DocumentChunk]:
    """将多个PageDocument对象的内容分割为多个DocumentChunk对象。"""
    chunks: list[DocumentChunk] = []

    for page in pages:
        chunks.extend(
            chunk_page(
                page=page,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    return chunks
