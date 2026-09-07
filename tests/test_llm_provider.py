from unittest.mock import MagicMock

from health_agent.core.config import Settings
from health_agent.llm.provider import LLMProvider


def create_test_settings() -> Settings:
    return Settings(
        llm_api_key="test-key",
        llm_base_url="https://example.com/v1",
        llm_model="test-model",
        llm_temperature=0.2,
        llm_timeout_seconds=10,
        llm_max_retries=0,
    )


def test_provider_initialization() -> None:
    provider = LLMProvider(settings=create_test_settings())

    assert provider.settings.llm_model == "test-model"
    assert provider.settings.llm_temperature == 0.2


def test_chat_response() -> None:
    provider = LLMProvider(settings=create_test_settings())

    mock_response = MagicMock()

    mock_response.model = "test-model"
    mock_response.choices[0].message.content = "测试回答"

    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    mock_response.usage.total_tokens = 15

    provider.client.chat.completions.create = MagicMock(return_value=mock_response)

    result = provider.chat(user_prompt="测试问题")

    assert result.content == "测试回答"
    assert result.model == "test-model"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 5
    assert result.total_tokens == 15


def test_chat_calls_expected_model() -> None:
    provider = LLMProvider(settings=create_test_settings())

    mock_response = MagicMock()
    mock_response.model = "test-model"
    mock_response.choices[0].message.content = "ok"
    mock_response.usage = None

    provider.client.chat.completions.create = MagicMock(return_value=mock_response)

    provider.chat(
        user_prompt="hello",
        system_prompt="system",
    )

    provider.client.chat.completions.create.assert_called_once()

    call_kwargs = provider.client.chat.completions.create.call_args.kwargs

    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"
