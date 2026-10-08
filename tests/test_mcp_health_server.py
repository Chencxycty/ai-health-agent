import asyncio

from mcp import Client

from health_agent.mcp.server import (
    mcp,
)


async def _test_list_tools() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()

        names = {tool.name for tool in tools.tools}

        assert "calculate_bmi" in names

        assert "calculate_average_blood_pressure" in names

        assert "calculate_average_glucose" in names


def test_list_tools() -> None:
    asyncio.run(_test_list_tools())


async def _test_bmi() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_bmi",
            {
                "height_cm": 175,
                "weight_kg": 80,
            },
        )

        assert result.is_error is False

        assert result.structured_content is not None


def test_bmi() -> None:
    asyncio.run(_test_bmi())
