from health_agent.agent.factory import (
    build_agent_service,
)


def print_result(
    title: str,
    result,
) -> None:
    print()
    print("=" * 80)

    print(title)

    print(
        "Route:",
        result.route,
    )

    print(
        "Steps:",
        result.steps,
    )

    print("Answer:")

    print(result.answer)

    print(
        "Sources:",
        result.sources,
    )


def main() -> None:
    agent = build_agent_service()

    thread_id = "conversation-demo-001"

    turn1 = agent.query(
        message="什么是高血压？",
        thread_id=thread_id,
    )

    print_result(
        "TURN 1",
        turn1,
    )

    turn2 = agent.query(
        message=("这种情况平时应该怎么监测？"),
        thread_id=thread_id,
    )

    print_result(
        "TURN 2",
        turn2,
    )


if __name__ == "__main__":
    main()
