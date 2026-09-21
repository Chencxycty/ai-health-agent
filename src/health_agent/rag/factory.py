from health_agent.core.config import (
    get_settings,
)
from health_agent.database.repositories import (
    DocumentChunkRepository,
)
from health_agent.database.session import (
    SessionLocal,
)
from health_agent.llm.provider import (
    LLMProvider,
)
from health_agent.rag.bm25_retriever import (
    BM25Retriever,
)
from health_agent.rag.hybrid_retriever import (
    HybridRetriever,
)
from health_agent.rag.mappers import (
    model_to_chunk,
)
from health_agent.rag.reranker import (
    Reranker,
)
from health_agent.rag.service import (
    RAGService,
)
from health_agent.rag.vector_retriever import (
    VectorRetriever,
)
from functools import lru_cache


def build_bm25_retriever() -> BM25Retriever:
    """构建BM25检索器。"""
    with SessionLocal() as session:
        repository = DocumentChunkRepository(session)

        models = repository.get_all()

    chunks = [model_to_chunk(model) for model in models]

    return BM25Retriever(chunks=chunks)


def build_hybrid_retriever(
    use_reranker: bool = True,
) -> HybridRetriever:
    """构建混合检索器 (Hybrid Retriever)。"""
    settings = get_settings()

    vector_retriever = VectorRetriever()

    bm25_retriever = build_bm25_retriever()

    reranker = None

    if use_reranker:
        reranker = Reranker(model_name=(settings.reranker_model))

    return HybridRetriever(
        vector_retriever=(vector_retriever),
        bm25_retriever=(bm25_retriever),
        reranker=reranker,
        candidate_k=20,
    )


@lru_cache(maxsize=1)
def build_rag_service() -> RAGService:
    """构建RAG（Retrieval-Augmented Generation）服务。"""
    retriever = build_hybrid_retriever(use_reranker=True)

    llm = LLMProvider()

    return RAGService(
        retriever=retriever,
        llm=llm,
    )
