from collections.abc import Iterator

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

from health_agent.core.config import Settings, get_settings
from health_agent.llm.exceptions import (
    LLMConnectionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from health_agent.llm.schemas import LLMResponse


class LLMProvider:
    """Unified interface for OpenAI-compatible language models."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        self.client = OpenAI(
            api_key=self.settings.llm_api_key,
            base_url=self.settings.llm_base_url,
            timeout=self.settings.llm_timeout_seconds,
            max_retries=self.settings.llm_max_retries,
        )

    def chat(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
    ) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=(
                    temperature
                    if temperature is not None
                    else self.settings.llm_temperature
                ),
            )

            content = response.choices[0].message.content or ""

            usage = response.usage

            return LLMResponse(
                content=content,
                model=response.model,
                prompt_tokens=(usage.prompt_tokens if usage is not None else None),
                completion_tokens=(
                    usage.completion_tokens if usage is not None else None
                ),
                total_tokens=(usage.total_tokens if usage is not None else None),
            )

        except APITimeoutError as exc:
            raise LLMTimeoutError("LLM request timed out.") from exc

        except RateLimitError as exc:
            raise LLMRateLimitError("LLM provider rate limit exceeded.") from exc

        except APIConnectionError as exc:
            raise LLMConnectionError("Unable to connect to LLM provider.") from exc

        except APIStatusError as exc:
            raise LLMProviderError(
                f"LLM provider returned HTTP {exc.status_code}."
            ) from exc

    def stream_chat(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float | None = None,
    ) -> Iterator[str]:
        try:
            stream = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                temperature=(
                    temperature
                    if temperature is not None
                    else self.settings.llm_temperature
                ),
                stream=True,
            )

            for chunk in stream:
                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    yield content

        except APITimeoutError as exc:
            raise LLMTimeoutError("Streaming request timed out.") from exc

        except RateLimitError as exc:
            raise LLMRateLimitError("LLM provider rate limit exceeded.") from exc

        except APIConnectionError as exc:
            raise LLMConnectionError("Unable to connect to LLM provider.") from exc

        except APIStatusError as exc:
            raise LLMProviderError(
                f"LLM provider returned HTTP {exc.status_code}."
            ) from exc
