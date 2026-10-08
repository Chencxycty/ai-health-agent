import asyncio
import sys
from pathlib import Path

from mcp import (
    Client,
    StdioServerParameters,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SERVER_PATH = PROJECT_ROOT / "scripts" / "mcp_basics_server.py"


async def main() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_PATH),
        ],
        cwd=str(PROJECT_ROOT),
    )

    async with Client(server) as client:
        print(
            "Protocol:",
            client.protocol_version,
        )

        tools = await client.list_tools()

        print("\nTOOLS")

        for tool in tools.tools:
            print(tool.name)

            print(tool.description)

            print(tool.input_schema)

        result = await client.call_tool(
            "add",
            {
                "a": 10,
                "b": 20,
            },
        )

        print("\nADD RESULT:")

        print(result.structured_content)

        resources = await client.list_resources()

        print("\nRESOURCES:")

        for resource in resources.resources:
            print(resource.uri)

        prompts = await client.list_prompts()

        print("\nPROMPTS:")

        for prompt in prompts.prompts:
            print(prompt.name)


if __name__ == "__main__":
    asyncio.run(main())
