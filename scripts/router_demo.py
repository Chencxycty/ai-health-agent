from health_agent.llm.provider import LLMProvider
from health_agent.llm.router import classify_intent


def main() -> None:
    llm = LLMProvider()

    queries = [
        "我175cm，80kg，BMI是多少？",
        "什么是高血压？",
        "你好，很高兴认识你。",
    ]

    for query in queries:
        result = classify_intent(
            llm=llm,
            query=query,
        )

        print()
        print("Query:", query)
        print("Intent:", result.intent)
        print("Confidence:", result.confidence)


if __name__ == "__main__":
    main()
