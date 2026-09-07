from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint.(起到一个信息筛选或过滤的作用)"""

    message: str = Field(
        min_length=1,
        max_length=5000,
        description="User message sent to the language model.",
    )


class ChatResponse(BaseModel):
    answer: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
