import json
from typing import Literal

from pydantic import BaseModel, Field

from health_agent.llm.provider import LLMProvider


class IntentResult(BaseModel):
    intent: Literal[
        "medical_knowledge",
        "health_calculation",
        "general_chat",
    ]
    confidence: float = Field(ge=0, le=1)


def classify_intent(
    llm: LLMProvider,
    query: str,
) -> IntentResult:
    response = llm.chat(
        system_prompt=(
            "Classify the user's request into exactly one category:\n"
            "- medical_knowledge\n"
            "- health_calculation\n"
            "- general_chat\n\n"
            "Return JSON only with fields:\n"
            "intent\n"
            "confidence"
        ),
        user_prompt=query,
        temperature=0,
    )

    data = json.loads(response.content)

    return IntentResult(**data)
