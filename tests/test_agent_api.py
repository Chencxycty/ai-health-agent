from dataclasses import dataclass

from fastapi.testclient import (
    TestClient,
)

from health_agent.api.dependencies import (
    get_agent_service,
)
from health_agent.api.main import app


@dataclass
class FakeAgentResult:
    answer: str = "测试回答"
    route: str = "general_chat"
    rag_query: str = ""
    tool_name: str | None = None
    sources: list = None
    steps: list = None
    interrupted: bool = False
    interrupt_payload: object = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []

        if self.steps is None:
            self.steps = [
                "prepare_turn",
                "risk_check",
                "router",
                "chat",
            ]


class FakeAgentService:
    def query(
        self,
        message: str,
        thread_id: str,
    ):
        return FakeAgentResult()

    def resume(
        self,
        thread_id: str,
        approved: bool,
    ):
        return FakeAgentResult()


client = TestClient(app)


def test_agent_query():
    app.dependency_overrides[get_agent_service] = lambda: FakeAgentService()

    try:
        response = client.post(
            "/agent/query",
            json={
                "message": "你好",
                "thread_id": "test-1",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["answer"] == "测试回答"

        assert data["route"] == "general_chat"

    finally:
        app.dependency_overrides.clear()
