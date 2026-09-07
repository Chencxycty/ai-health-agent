from health_agent.llm.provider import LLMProvider


def main() -> None:
    llm = LLMProvider()

    print("Assistant: ", end="", flush=True)

    for token in llm.stream_chat(
        system_prompt=("你是一名健康信息助手，请使用准确、简洁的中文回答。"),
        user_prompt="请简单介绍家庭血压监测的重要性。",
    ):
        print(token, end="", flush=True)

    print()


if __name__ == "__main__":
    main()
