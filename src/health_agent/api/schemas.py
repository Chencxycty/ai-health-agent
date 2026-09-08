from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    """Pydantic Schema for the chat request. This model is used to validate the incoming request data for the chat endpoint. It ensures that the message field is a non-empty string with a maximum length of 5000 characters. This validation helps prevent empty or excessively long messages from being processed by the language model, which could lead to errors or unexpected behavior. In essence, it acts as a filter to ensure that only valid and appropriately sized messages are sent to the language model for processing.
    (起到一个信息筛选或过滤的作用)"""

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
