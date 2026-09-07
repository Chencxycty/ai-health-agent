from fastapi.testclient import TestClient

from health_agent.api.dependencies import get_llm_provider
from health_agent.api.main import app
from health_agent.llm.exceptions import LLMTimeoutError
from health_agent.llm.schemas import LLMResponse

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_chat_rejects_empty_message() -> None:
    response = client.post(
        "/chat",
        json={
            "message": "",
        },
    )

    assert response.status_code == 422


class FakeLLMProvider:
    def chat(
        self,
        user_prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
    ) -> LLMResponse:
        return LLMResponse(
            content="这是测试回答。",
            model="fake-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
        )


def test_chat_success() -> None:
    app.dependency_overrides[get_llm_provider] = lambda: FakeLLMProvider()

    try:
        response = client.post(
            "/chat",
            json={
                "message": "什么是高血压？",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["answer"] == "这是测试回答。"
        assert data["model"] == "fake-model"
        assert data["total_tokens"] == 15

    finally:
        app.dependency_overrides.clear()


class TimeoutLLMProvider:
    def chat(
        self,
        user_prompt: str,
        system_prompt: str = "",
        temperature: float | None = None,
    ) -> LLMResponse:
        raise LLMTimeoutError("Test timeout")


def test_chat_timeout() -> None:
    app.dependency_overrides[get_llm_provider] = lambda: TimeoutLLMProvider()

    try:
        response = client.post(
            "/chat",
            json={
                "message": "测试",
            },
        )

        assert response.status_code == 504

        data = response.json()

        assert data["error"] == "llm_timeout"

    finally:
        app.dependency_overrides.clear()
