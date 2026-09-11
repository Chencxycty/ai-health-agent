from health_agent.llm.schemas import (
    LLMResponse,
)
from health_agent.rag.schemas import (
    DocumentChunk,
    SearchResult,
)
from health_agent.rag.service import (
    RAGService,
)


class FakeRetriever:
    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        return [
            SearchResult(
                chunk=DocumentChunk(
                    chunk_id="chunk-1",
                    document_id="doc-1",
                    title="高血压指南",
                    source="test.pdf",
                    page=12,
                    chunk_index=0,
                    content=("高血压患者可进行家庭血压监测。"),
                ),
                score=0.9,
            )
        ]


class FakeLLMProvider:
    def chat(
        self,
        user_prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
    ) -> LLMResponse:
        assert "[Source 1]" in (user_prompt)

        return LLMResponse(
            content=("可进行家庭血压监测。[Source 1]"),
            model="fake-model",
            prompt_tokens=100,
            completion_tokens=20,
            total_tokens=120,
        )


def test_rag_service_returns_answer_and_citation() -> None:
    service = RAGService(
        retriever=FakeRetriever(),
        llm=FakeLLMProvider(),
    )

    result = service.answer("如何监测血压？")

    assert "[Source 1]" in result.answer

    assert result.model == "fake-model"

    assert len(result.citations) == 1

    assert result.citations[0].page == 12

    assert result.total_tokens == 120
