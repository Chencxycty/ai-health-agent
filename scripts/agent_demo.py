from health_agent.agent.factory import (
    build_agent_service,
)


def main():
    agent = build_agent_service()

    cases = [
        "你好",
        "什么是高血压？",
        "我175cm，80kg，BMI是多少？",
    ]

    for query in cases:
        result = agent.query(
            message=query,
            thread_id=(f"demo-{query}"),
        )

        print()
        print(query)
        print(result.route)
        print(result.tool_name)
        print(result.answer)
        print(result.steps)


if __name__ == "__main__":
    main()
