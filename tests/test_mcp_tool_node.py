from dataclasses import dataclass

from health_agent.agent.nodes import (
    AgentNodes,
)


@dataclass
class FakeToolCall:
    name: str
    arguments: dict


@dataclass
class FakeMCPResult:
    name: str
    data: object
    is_error: bool = False
    error: str | None = None


class FakeLLM:
    def choose_tool(
        self,
        user_prompt,
        tools,
    ):
        assert tools

        return FakeToolCall(
            name="calculate_bmi",
            arguments={
                "height_cm": 175,
                "weight_kg": 80,
            },
        )


class FakeMCPClient:
    def openai_tool_schemas(
        self,
    ):
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_bmi",
                    "description": "Calculate BMI.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "height_cm": {"type": "number"},
                            "weight_kg": {"type": "number"},
                        },
                        "required": [
                            "height_cm",
                            "weight_kg",
                        ],
                    },
                },
            }
        ]

    def call_tool(
        self,
        name,
        arguments,
    ):
        assert name == "calculate_bmi"

        assert arguments["height_cm"] == 175

        return FakeMCPResult(
            name=name,
            data={"result": {"bmi": 26.12}},
        )


class FakeRAGService:
    pass


def test_tool_node_calls_mcp():
    nodes = AgentNodes(
        llm=FakeLLM(),
        rag_service=(FakeRAGService()),
        mcp_client=(FakeMCPClient()),
    )

    result = nodes.tool_node(
        {
            "user_message": ("我175cm，80kg，BMI是多少？"),
            "steps": [],
        }
    )

    assert result["tool_name"] == "calculate_bmi"

    assert result["tool_error"] is None

    assert "mcp_tool:calculate_bmi" in result["steps"]
