from health_agent.core.config import get_settings
from health_agent.database.repositories import (
    DocumentChunkRepository,
)
from health_agent.database.session import SessionLocal
from health_agent.rag.embeddings import EmbeddingModel
from health_agent.rag.mappers import model_to_chunk
from health_agent.rag.schemas import SearchResult


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
        document_id: str | None = None,
    ) -> list[SearchResult]:
        """使用向量搜索查找与查询最相似的文档块。"""
        query_embedding = self.embedding_model.embed_query(query)

        with SessionLocal() as session:
            repository = DocumentChunkRepository(session)

            rows = repository.vector_search(
                query_embedding=(query_embedding.tolist()),
                top_k=top_k,
                document_id=document_id,
            )

        return [
            SearchResult(
                chunk=model_to_chunk(model),
                score=score,
            )
            for model, score in rows
        ]
