from functools import lru_cache

from health_agent.llm.provider import LLMProvider
from health_agent.rag.factory import (
    build_rag_service,
)
from health_agent.rag.service import (
    RAGService,
)


@lru_cache
def get_llm_provider() -> LLMProvider:
    return LLMProvider()


@lru_cache
def get_rag_service() -> RAGService:
    return build_rag_service()
