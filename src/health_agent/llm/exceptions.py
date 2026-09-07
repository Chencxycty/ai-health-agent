class LLMError(Exception):
    """Base exception for all LLM-related failures."""


class LLMTimeoutError(LLMError):
    """The model request timed out."""


class LLMConnectionError(LLMError):
    """Unable to connect to the model provider."""


class LLMRateLimitError(LLMError):
    """The model provider rate limit was reached."""


class LLMProviderError(LLMError):
    """The provider returned an unexpected error."""


# class LLMIllegalError(LLMError):
#     """The request contained illegal content."""
