from dataclasses import dataclass, field
from typing import Any

from fastapi.testclient import TestClient

from health_agent.api.dependencies import get_agent_service
from health_agent.api.main import app


@dataclass
class ContractResult:
    answer: str = "contract answer"
    route: str = "medical_knowledge"
    rag_query: str = "normalized query"
    tool_name: str | None = None
    sources: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "source_id": 1,
                "title": "Guide",
                "page": 2,
                "chunk_id": "chunk-001",
            }
        ]
    )
    steps: list[str] = field(default_factory=lambda: ["prepare_turn", "rag"])
    interrupted: bool = False
    interrupt_payload: Any | None = None


class RecordingAgentService:
    def __init__(self) -> None:
        self.query_call: tuple[str, str] | None = None
        self.resume_call: tuple[str, bool] | None = None

    def query(self, message: str, thread_id: str) -> ContractResult:
        self.query_call = (message, thread_id)
        return ContractResult()

    def resume(self, thread_id: str, approved: bool) -> ContractResult:
        self.resume_call = (thread_id, approved)
        return ContractResult(answer="safe answer", route="unclassified", sources=[])


client = TestClient(app)


def test_agent_query_contract() -> None:
    service = RecordingAgentService()
    app.dependency_overrides[get_agent_service] = lambda: service

    try:
        response = client.post(
            "/agent/query",
            json={"message": "What is hypertension?", "thread_id": "contract-1"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.query_call == ("What is hypertension?", "contract-1")
    assert response.json() == {
        "answer": "contract answer",
        "route": "medical_knowledge",
        "tool_name": None,
        "sources": [
            {
                "source_id": 1,
                "title": "Guide",
                "page": 2,
                "chunk_id": "chunk-001",
            }
        ],
        "steps": ["prepare_turn", "rag"],
        "interrupted": False,
        "interrupt_payload": None,
    }


def test_agent_resume_contract_uses_original_thread() -> None:
    service = RecordingAgentService()
    app.dependency_overrides[get_agent_service] = lambda: service

    try:
        response = client.post(
            "/agent/resume",
            json={"thread_id": "contract-1", "approved": False},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert service.resume_call == ("contract-1", False)
    assert response.json()["answer"] == "safe answer"


def test_agent_thread_id_constraints_are_consistent() -> None:
    service = RecordingAgentService()
    app.dependency_overrides[get_agent_service] = lambda: service

    try:
        empty_resume = client.post(
            "/agent/resume",
            json={"thread_id": "", "approved": False},
        )
        long_query = client.post(
            "/agent/query",
            json={"message": "hello", "thread_id": "x" * 201},
        )
    finally:
        app.dependency_overrides.clear()

    assert empty_resume.status_code == 422
    assert long_query.status_code == 422
    assert service.query_call is None
    assert service.resume_call is None
