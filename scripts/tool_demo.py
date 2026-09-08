from health_agent.llm.provider import LLMProvider
from health_agent.tools.registry import (
    TOOLS,
    execute_tool,
)


def main() -> None:
    llm = LLMProvider()

    query = "我身高175cm，体重80kg，帮我算BMI。"

    tool_call = llm.choose_tool(
        user_prompt=query,
        tools=TOOLS,
    )

    if tool_call is None:
        print("No tool selected.")
        return

    print(f"Selected tool: {tool_call.name}")

    print(f"Arguments: {tool_call.arguments}")

    result = execute_tool(
        name=tool_call.name,
        arguments=tool_call.arguments,
    )

    print(f"Tool result: {result}")

    final_response = llm.chat(
        system_prompt=(
            "你是一名健康信息助手。"
            "工具计算结果是确定性结果，"
            "请基于结果进行简洁说明。"
            "不要进行医疗诊断。"
        ),
        user_prompt=(
            f"用户问题：{query}\n"
            f"工具：{tool_call.name}\n"
            f"工具结果：{result}\n"
            "请给出最终回答。"
        ),
    )

    print(final_response.content)


if __name__ == "__main__":
    main()
