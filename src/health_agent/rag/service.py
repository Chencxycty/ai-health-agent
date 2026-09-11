import time

from health_agent.llm.provider import (
    LLMProvider,
)
from health_agent.rag.context_builder import (
    build_context,
)
from health_agent.rag.schemas import (
    Citation,
    RAGAnswer,
)

SYSTEM_PROMPT = """
你是一名严谨的健康信息助手。

你必须仅根据提供的参考资料回答用户的问题。

规则：
1. 不得把参考资料之外的事实作为回答依据。
2. 如果参考资料不足以回答问题，请明确说明：
   “根据当前提供的资料无法确定。”
3. 不得虚构医学事实、指南名称、数字、页码或出处。
4. 每个关键结论尽量使用 [Source N] 标明依据。
5. 不进行个体疾病诊断。
6. 不替代医生提供诊疗建议。
7. 回答应准确、清晰、简洁。
""".strip()


class RAGService:
    """RAG（Retrieval-Augmented Generation）服务类，用于处理用户查询，检索相关文档块，并生成回答。"""

    def __init__(
        self,
        retriever,
        llm: LLMProvider,
    ) -> None:
        self.retriever = retriever
        self.llm = llm

    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> RAGAnswer:
        """处理用户查询，检索相关文档块，并生成回答。"""
        total_start = time.perf_counter()

        retrieval_start = time.perf_counter()

        # 使用混合检索器进行查询
        results = self.retriever.search(
            query=query,
            top_k=top_k,
        )

        retrieval_latency_ms = (time.perf_counter() - retrieval_start) * 1000

        # 构建上下文字符串
        context = build_context(results)

        generation_start = time.perf_counter()

        # 使用LLM生成回答
        response = self.llm.chat(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=(f"用户问题：\n{query}\n\n参考资料：\n{context}"),
            temperature=0.1,
        )

        generation_latency_ms = (time.perf_counter() - generation_start) * 1000

        total_latency_ms = (time.perf_counter() - total_start) * 1000

        # 构建引用信息列表
        citations = [
            Citation(
                source_id=index,
                title=result.chunk.title,
                page=result.chunk.page,
                chunk_id=(result.chunk.chunk_id),
            )
            for index, result in enumerate(
                results,
                start=1,
            )
        ]

        # 构建并返回 RAGAnswer 对象（包含生成的回答和引用信息）
        return RAGAnswer(
            answer=response.content,
            model=response.model,
            citations=citations,
            prompt_tokens=(response.prompt_tokens),
            completion_tokens=(response.completion_tokens),
            total_tokens=(response.total_tokens),
            retrieval_latency_ms=(retrieval_latency_ms),
            generation_latency_ms=(generation_latency_ms),
            total_latency_ms=(total_latency_ms),
        )
