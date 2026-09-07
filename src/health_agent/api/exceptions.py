from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from health_agent.llm.exceptions import (
    LLMConnectionError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    # LLMIllegalError
)

"""Register exception handlers for the FastAPI application.
This module defines custom exception handlers for various LLM-related errors.（有错误代码和对应的错误类型）"""


def register_exception_handlers(app: FastAPI) -> None:
    # FastAPI 的异常处理机制，定义了针对不同 LLM 异常的处理函数，并返回相应的 JSON 响应。
    # FastAPI 支持通过 @app.exception_handler() 注册全局异常处理器
    @app.exception_handler(LLMTimeoutError)
    async def handle_llm_timeout(
        request: Request,
        exc: LLMTimeoutError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=504,
            content={
                "error": "llm_timeout",
                "message": str(exc),
            },
        )

    @app.exception_handler(LLMRateLimitError)
    async def handle_llm_rate_limit(
        request: Request,
        exc: LLMRateLimitError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "error": "llm_rate_limit",
                "message": str(exc),
            },
        )

    @app.exception_handler(LLMConnectionError)
    async def handle_llm_connection(
        request: Request,
        exc: LLMConnectionError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "error": "llm_connection_error",
                "message": str(exc),
            },
        )

    @app.exception_handler(LLMProviderError)
    async def handle_llm_provider(
        request: Request,
        exc: LLMProviderError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={
                "error": "llm_provider_error",
                "message": str(exc),
            },
        )

    # @app.exception_handler(LLMIllegalError)
    # async def handle_llm_illegal(
    #     request: Request,
    #     exc: LLMIllegalError,
    # ) -> JSONResponse:
    #     return JSONResponse(
    #         status_code=422,
    #         content={
    #             "error": "llm_illegal_error",
    #             "message": str(exc),
    #         },
    #     )
