import argparse
import json
from dataclasses import (
    asdict,
    is_dataclass,
)
from typing import Any

from mcp.server import MCPServer
from pydantic import BaseModel

from health_agent.tools.registry import (
    execute_tool,
)


mcp = MCPServer(
    "AI Health Agent Tools",
    instructions=(
        "Provides deterministic health "
        "calculation tools. "
        "These tools do not perform "
        "medical diagnosis."
    ),
)


def _to_jsonable(
    value: Any,
) -> Any:
    if isinstance(
        value,
        BaseModel,
    ):
        return value.model_dump()

    if is_dataclass(value):
        return asdict(value)

    if isinstance(
        value,
        dict,
    ):
        return {key: _to_jsonable(item) for key, item in value.items()}

    if isinstance(
        value,
        (list, tuple),
    ):
        return [_to_jsonable(item) for item in value]

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if value is None:
        return None

    return str(value)


@mcp.tool()
def calculate_bmi(
    height_cm: float,
    weight_kg: float,
) -> dict[str, Any]:
    """
    Calculate body mass index (BMI)
    from height in centimeters and
    weight in kilograms.

    This tool only performs deterministic
    calculation and does not diagnose disease.
    """
    result = execute_tool(
        name="calculate_bmi",
        arguments={
            "height_cm": height_cm,
            "weight_kg": weight_kg,
        },
    )

    return {
        "tool": "calculate_bmi",
        "result": _to_jsonable(result),
    }


@mcp.tool()
def calculate_average_blood_pressure(
    readings: list[dict[str, float]],
) -> dict[str, Any]:
    """
    Calculate average systolic and
    diastolic blood pressure from
    multiple readings.

    Each reading must contain
    systolic and diastolic values.
    """
    result = execute_tool(
        name=("calculate_average_blood_pressure"),
        arguments={
            "readings": readings,
        },
    )

    return {
        "tool": ("calculate_average_blood_pressure"),
        "result": _to_jsonable(result),
    }


@mcp.tool()
def calculate_average_glucose(
    values: list[float],
) -> dict[str, Any]:
    """
    Calculate the arithmetic mean
    of glucose measurements.

    This tool only performs
    deterministic calculation.
    """
    result = execute_tool(
        name=("calculate_average_glucose"),
        arguments={
            "values": values,
        },
    )

    return {
        "tool": ("calculate_average_glucose"),
        "result": _to_jsonable(result),
    }


@mcp.resource("health://capabilities")
def health_capabilities() -> str:
    """
    Describe the capabilities and
    limitations of this MCP server.
    """
    data = {
        "server": "AI Health Agent Tools",
        "tools": [
            "calculate_bmi",
            ("calculate_average_blood_pressure"),
            ("calculate_average_glucose"),
        ],
        "limitations": [
            ("No medical diagnosis"),
            ("No medication recommendation"),
            ("Deterministic calculations only"),
        ],
    }

    return json.dumps(
        data,
        ensure_ascii=False,
        indent=2,
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--transport",
        choices=[
            "stdio",
            "streamable-http",
        ],
        default="stdio",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8100,
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()

        return

    mcp.run(
        transport=("streamable-http"),
        host=args.host,
        port=args.port,
        # Day 16这个服务本身
        # 不需要服务端MCP session状态
        stateless_http=True,
        # 简化HTTP响应
        json_response=True,
    )


if __name__ == "__main__":
    main()
