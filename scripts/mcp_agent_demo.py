from uuid import uuid4

from health_agent.agent.factory import (
    build_agent_service,
)


def main() -> None:
    agent = build_agent_service()

    cases = [
        ("我身高175cm，体重80kg，BMI是多少？"),
        ("我的血压分别是130/80、140/90、135/85，平均血压是多少？"),
        ("最近三次血糖是5.6、6.1、5.9，平均是多少？"),
    ]

    for query in cases:
        result = agent.query(
            message=query,
            thread_id=(f"mcp-demo-{uuid4()}"),
        )

        print()
        print("=" * 80)

        print("QUERY:")

        print(query)

        print(
            "ROUTE:",
            result.route,
        )

        print(
            "TOOL:",
            result.tool_name,
        )

        print(
            "STEPS:",
            result.steps,
        )

        print("ANSWER:")

        print(result.answer)


if __name__ == "__main__":
    main()
