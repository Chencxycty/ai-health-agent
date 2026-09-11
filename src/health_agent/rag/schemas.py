from dataclasses import dataclass


@dataclass(frozen=True)
class PageDocument:
    """表示文档的单页内容，包括文档ID、标题、来源、页码和内容。"""

    document_id: str
    title: str
    source: str
    page: int
    content: str


@dataclass(frozen=True)
class DocumentChunk:
    """表示文档的一个分块内容，包括分块ID、所属文档ID、标题、来源、页码、分块索引和内容。"""

    chunk_id: str
    document_id: str
    title: str
    source: str
    page: int
    chunk_index: int
    content: str


@dataclass(frozen=True)
class SearchResult:
    """表示搜索结果，包括文档分块和相关性评分。(搜索结果+相似度)"""

    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class Citation:
    """表示引用信息，包括来源ID、标题、页码和分块ID。"""

    source_id: int
    title: str
    page: int
    chunk_id: str


@dataclass(frozen=True)
class RAGAnswer:
    """表示RAG（Retrieval-Augmented Generation）模型的回答，包括答案文本、使用的模型、引用信息以及相关的令牌和延迟信息。"""

    answer: str
    model: str
    citations: list[Citation]

    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
