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
    """响应模型，用于封装语言模型的回答和相关信息。"""

    answer: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class RAGQueryRequest(BaseModel):
    """RAG查询请求模型，用于封装用户的查询请求。"""

    query: str = Field(
        min_length=1,
        max_length=5000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )


class CitationResponse(BaseModel):
    """引用信息响应模型，用于封装文档引用的相关信息。"""

    source_id: int
    title: str
    page: int
    chunk_id: str


class RAGQueryResponse(BaseModel):
    """RAG查询响应模型，用于封装RAG模型的回答和相关信息。"""

    answer: str
    model: str

    sources: list[CitationResponse]

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    retrieval_latency_ms: float
    generation_latency_ms: float
    total_latency_ms: float
