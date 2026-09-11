from health_agent.rag.bm25_retriever import BM25Retriever
from health_agent.rag.fusion import reciprocal_rank_fusion
from health_agent.rag.reranker import Reranker
from health_agent.rag.schemas import SearchResult
from health_agent.rag.vector_retriever import VectorRetriever


class HybridRetriever:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        bm25_retriever: BM25Retriever,
        reranker: Reranker | None = None,
        candidate_k: int = 20,
    ) -> None:
        self.vector_retriever = vector_retriever

        self.bm25_retriever = bm25_retriever

        self.reranker = reranker

        self.candidate_k = candidate_k

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """使用混合检索方法 (向量检索 + BM25检索(关键词检索) + Reranker) 查找与查询最相关的文档块。"""
        vector_results = self.vector_retriever.search(
            query=query,
            top_k=self.candidate_k,
        )

        bm25_results = self.bm25_retriever.search(
            query=query,
            top_k=self.candidate_k,
        )

        fused_results = reciprocal_rank_fusion(
            [
                vector_results,
                bm25_results,
            ],
            top_k=self.candidate_k,
        )

        if self.reranker is None:
            return fused_results[:top_k]

        return self.reranker.rerank(
            query=query,
            results=fused_results,
            top_k=top_k,
        )
