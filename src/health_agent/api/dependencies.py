from functools import lru_cache

from health_agent.llm.provider import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    return LLMProvider()
