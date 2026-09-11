from health_agent.database.models import (
    DocumentChunkModel,
)
from health_agent.rag.schemas import DocumentChunk


def model_to_chunk(
    model: DocumentChunkModel,
) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=model.chunk_id,
        document_id=model.document_id,
        title=model.title,
        source=model.source,
        page=model.page,
        chunk_index=model.chunk_index,
        content=model.content,
    )
