import numpy as np

from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


def cosine_search(
    query_embedding: np.ndarray,
    document_embeddings: np.ndarray,
    chunks: list[DocumentChunk],
    top_k: int = 5,
) -> list[SearchResult]:
    """使用余弦相似度进行向量搜索，返回与查询最相关的文档块。"""
    if len(chunks) != len(document_embeddings):
        raise ValueError("chunks and document_embeddings must have the same length.")

    scores = document_embeddings @ query_embedding

    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        SearchResult(
            chunk=chunks[index],
            score=float(scores[index]),
        )
        for index in top_indices
    ]
