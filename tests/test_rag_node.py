from dataclasses import dataclass
from unittest.mock import AsyncMock

from health_agent.agent.nodes import (
    AgentNodes,
)


@dataclass
class FakeCitation:
    source_id: int
    title: str
    page: int
    chunk_id: str


@dataclass
class FakeRAGAnswer:
    answer: str
    citations: list[FakeCitation]
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    total_tokens: int | None = None


class FakeRAGService:
    def answer(
        self,
        query: str,
        top_k: int = 5,
    ) -> FakeRAGAnswer:
        assert query == "什么是高血压？"

        return FakeRAGAnswer(
            answer="高血压是一种慢性健康问题。[Source 1]",
            citations=[
                FakeCitation(
                    source_id=1,
                    title="高血压指南",
                    page=10,
                    chunk_id="chunk-001",
                )
            ],
        )


class FakeLLM:
    pass


def test_rag_node() -> None:
    nodes = AgentNodes(
        llm=FakeLLM(),
        rag_service=FakeRAGService(),
        mcp_client=AsyncMock(),
    )

    result = nodes.rag_node(
        {
            "user_message": "什么是高血压？",
            "steps": [],
        }
    )

    assert "高血压" in result["final_answer"]

    assert len(result["sources"]) == 1

    assert result["sources"][0]["page"] == 10

    assert "rag" in result["steps"]
