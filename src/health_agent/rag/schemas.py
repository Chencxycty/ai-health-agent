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
