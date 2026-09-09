from health_agent.core.config import get_settings
from health_agent.database.repositories import (
    DocumentChunkRepository,
)
from health_agent.database.session import SessionLocal
from health_agent.rag.embeddings import EmbeddingModel
from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


class VectorRetriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        settings = get_settings()

        self.embedding_model = embedding_model or EmbeddingModel(
            settings.embedding_model
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        query_embedding = self.embedding_model.embed_query(query)

        with SessionLocal() as session:
            repository = DocumentChunkRepository(session)

            rows = repository.vector_search(
                query_embedding=query_embedding.tolist(),
                top_k=top_k,
            )

        results: list[SearchResult] = []

        for model, score in rows:
            chunk = DocumentChunk(
                chunk_id=model.chunk_id,
                document_id=model.document_id,
                title=model.title,
                source=model.source,
                page=model.page,
                chunk_index=model.chunk_index,
                content=model.content,
            )

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=score,
                )
            )

        return results
