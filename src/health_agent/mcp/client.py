import asyncio
from typing import Any

from mcp import Client

from health_agent.mcp.schemas import (
    MCPToolInfo,
    MCPToolResult,
)


class HealthMCPClient:
    def __init__(
        self,
        server_url: str,
    ) -> None:
        self.server_url = server_url

        self._tool_cache: list[MCPToolInfo] | None = None

    async def alist_tools(
        self,
    ) -> list[MCPToolInfo]:
        async with Client(self.server_url) as client:
            response = await client.list_tools()

        return [
            MCPToolInfo(
                name=tool.name,
                description=(tool.description or ""),
                input_schema=(tool.input_schema),
            )
            for tool in response.tools
        ]

    async def acall_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> MCPToolResult:
        async with Client(self.server_url) as client:
            result = await client.call_tool(
                name,
                arguments,
            )

        if result.is_error:
            error_text = self._content_to_text(result.content)

            return MCPToolResult(
                name=name,
                data=None,
                is_error=True,
                error=error_text,
            )

        data: Any

        if result.structured_content is not None:
            data = result.structured_content

        else:
            data = self._content_to_text(result.content)

        return MCPToolResult(
            name=name,
            data=data,
        )

    async def aopenai_tool_schemas(
        self,
    ) -> list[dict[str, Any]]:
        tools = await self.alist_tools()

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    def list_tools(
        self,
    ) -> list[MCPToolInfo]:
        return asyncio.run(self.alist_tools())

    def call_tool(
        self,
        name: str,
        arguments: dict[str, Any],
    ) -> MCPToolResult:
        return asyncio.run(
            self.acall_tool(
                name=name,
                arguments=arguments,
            )
        )

    def openai_tool_schemas(
        self,
    ) -> list[dict[str, Any]]:
        if self._tool_cache is None:
            self._tool_cache = self.list_tools()

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self._tool_cache
        ]

    @staticmethod
    def _content_to_text(
        content,
    ) -> str:
        texts: list[str] = []

        for block in content:
            text = getattr(
                block,
                "text",
                None,
            )

            if text is not None:
                texts.append(text)

        return "\n".join(texts)
