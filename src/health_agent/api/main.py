import logging
import time

from fastapi import Depends, FastAPI

from health_agent.api.dependencies import (
    get_llm_provider,
    get_rag_service,
)
from health_agent.api.exceptions import register_exception_handlers
from health_agent.api.schemas import (
    ChatRequest,
    ChatResponse,
    CitationResponse,
    HealthResponse,
    RAGQueryRequest,
    RAGQueryResponse,
)
from health_agent.core.logging import configure_logging
from health_agent.llm.provider import LLMProvider
from health_agent.rag.service import (
    RAGService,
)

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Health Agent API",
    version="0.1.0",
    description="Backend API for the AI Health Agent project.",
)
register_exception_handlers(app)


# 定义API端点和路由
@app.get(
    "/health",
    response_model=HealthResponse,
)
# 定义健康检查端点，返回服务状态
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


# 定义聊天端点，接收用户消息并返回模型生成的回答
@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    llm: LLMProvider = Depends(get_llm_provider),
) -> ChatResponse:
    """处理聊天请求，调用语言模型生成回答。"""
    start_time = time.perf_counter()
    logger.info("Chat request started")

    response = llm.chat(
        system_prompt=(
            "你是一名严谨的健康信息助手。"
            "请使用清晰、准确、简洁的中文回答问题。"
            "不要冒充医生进行诊断。"
        ),
        user_prompt=request.message,
    )

    latency_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "Chat request completed model=%s latency_ms=%.2f tokens=%s",
        response.model,
        latency_ms,
        response.total_tokens,
    )

    return ChatResponse(
        answer=response.content,
        model=response.model,
        prompt_tokens=response.prompt_tokens,
        completion_tokens=response.completion_tokens,
        total_tokens=response.total_tokens,
    )


# 定义RAG查询端点，接收用户查询并返回RAG模型生成的回答和引用信息
@app.post(
    "/rag/query",
    response_model=RAGQueryResponse,
)
def rag_query(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> RAGQueryResponse:
    """处理RAG查询请求，调用RAG服务生成回答和引用信息。"""
    result = rag_service.answer(
        query=request.query,
        top_k=request.top_k,
    )

    return RAGQueryResponse(
        answer=result.answer,
        model=result.model,
        sources=[
            CitationResponse(
                source_id=citation.source_id,
                title=citation.title,
                page=citation.page,
                chunk_id=(citation.chunk_id),
            )
            for citation in result.citations
        ],
        prompt_tokens=(result.prompt_tokens),
        completion_tokens=(result.completion_tokens),
        total_tokens=(result.total_tokens),
        retrieval_latency_ms=(result.retrieval_latency_ms),
        generation_latency_ms=(result.generation_latency_ms),
        total_latency_ms=(result.total_latency_ms),
    )
