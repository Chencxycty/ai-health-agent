import json
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
from health_agent.llm.schemas import (
    LLMResponse,
    LLMToolCall,
)


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
        """与 LLM 进行对话的函数。根据用户的提示和系统提示，调用 LLM 来生成响应。"""
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

    def choose_tool(
        self,
        user_prompt: str,
        tools: list[dict],
    ) -> LLMToolCall | None:
        """响应时选择工具的函数。根据用户的提示和可用工具列表，调用 LLM 来选择最合适的工具。
        如果 LLM 返回了工具调用信息，则解析并返回 LLMToolCall 对象；如果没有工具调用信息，则返回 None。"""
        try:
            response = self.client.chat.completions.create(
                model=self.settings.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a routing assistant. "
                            "Use a tool only when the user's request "
                            "requires a deterministic calculation."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                tools=tools,
                tool_choice="auto",
                temperature=0,
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return None

            tool_call = message.tool_calls[0]

            arguments = json.loads(tool_call.function.arguments)

            return LLMToolCall(
                id=tool_call.id,
                name=tool_call.function.name,
                arguments=arguments,
            )

        except json.JSONDecodeError as exc:
            raise LLMProviderError("Model returned invalid tool arguments.") from exc

        except APITimeoutError as exc:
            raise LLMTimeoutError("Tool selection request timed out.") from exc

        except RateLimitError as exc:
            raise LLMRateLimitError("LLM provider rate limit exceeded.") from exc

        except APIConnectionError as exc:
            raise LLMConnectionError("Unable to connect to LLM provider.") from exc

        except APIStatusError as exc:
            raise LLMProviderError(
                f"LLM provider returned HTTP {exc.status_code}."
            ) from exc
