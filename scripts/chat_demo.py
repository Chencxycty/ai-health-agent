from health_agent.llm.provider import LLMProvider


def main() -> None:
    llm = LLMProvider()

    response = llm.chat(
        # 系统prompt用于设定助手的行为和回答风格，用户prompt是用户输入的问题或请求。
        system_prompt=(
            "你是一名严谨的健康信息助手。"
            "回答健康问题时使用清晰、简洁的中文。"
            "不要冒充医生进行诊断。"
        ),
        user_prompt="请用100字以内解释什么是高血压。",
    )

    print("\n=== Response ===")
    print(response.content)

    print("\n=== Metadata ===")
    print(f"Model: {response.model}")
    print(f"Prompt tokens: {response.prompt_tokens}")
    print(f"Completion tokens: {response.completion_tokens}")
    print(f"Total tokens: {response.total_tokens}")


if __name__ == "__main__":
    main()
