from health_agent.agent.factory import (
    build_agent_service,
)


def main() -> None:
    agent = build_agent_service()

    thread_id = "hitl-demo-001"

    result = agent.query(
        message=("我突然出现剧烈胸痛，现在应该怎么办？"),
        thread_id=thread_id,
    )

    print(
        "Interrupted:",
        result.interrupted,
    )

    print(
        "Payload:",
        result.interrupt_payload,
    )

    print(
        "Steps:",
        result.steps,
    )

    if result.interrupted:
        result = agent.resume(
            thread_id=thread_id,
            approved=False,
        )

        print()
        print("RESUMED")
        print(result.answer)

        print(result.steps)


if __name__ == "__main__":
    main()
