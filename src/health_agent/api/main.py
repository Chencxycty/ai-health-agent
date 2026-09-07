import logging
import time

from fastapi import Depends, FastAPI

from health_agent.api.dependencies import get_llm_provider
from health_agent.api.exceptions import register_exception_handlers
from health_agent.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
)
from health_agent.core.logging import configure_logging
from health_agent.llm.provider import LLMProvider

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Health Agent API",
    version="0.1.0",
    description="Backend API for the AI Health Agent project.",
)
register_exception_handlers(app)


@app.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    llm: LLMProvider = Depends(get_llm_provider),
) -> ChatResponse:
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
