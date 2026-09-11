import jieba
from rank_bm25 import BM25Okapi

from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)


def tokenize(
    text: str,
) -> list[str]:
    """对文本进行分词处理。"""
    return [token.strip() for token in jieba.lcut(text.lower()) if token.strip()]


class BM25Retriever:
    """使用BM25算法进行文档检索。(关键词检索)"""

    def __init__(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        if not chunks:
            raise ValueError("BM25 corpus cannot be empty.")

        self.chunks = chunks

        self.tokenized_corpus = [tokenize(chunk.content) for chunk in chunks]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 20,
    ) -> list[SearchResult]:
        """使用BM25算法检索与查询最相关的文档块。"""
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query_tokens = tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        return [
            SearchResult(
                chunk=self.chunks[index],
                score=float(scores[index]),
            )
            for index in ranked_indices
        ]
