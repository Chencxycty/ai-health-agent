import operator
from typing import Annotated, Any, Literal, TypedDict


AgentRoute = Literal[
    "unclassified",
    "medical_knowledge",
    "health_calculation",
    "general_chat",
]

RiskLevel = Literal[
    "unknown",
    "normal",
    "high",
]


class AgentState(TypedDict, total=False):
    # ---------- Persistent ----------
    messages: Annotated[
        list[dict[str, str]],
        operator.add,
    ]

    # ---------- Current turn ----------
    user_message: str

    # Router
    route: AgentRoute
    confidence: float

    # Risk / HITL
    risk_level: RiskLevel
    risk_reason: str
    review_required: bool
    review_approved: bool

    # RAG
    rag_query: str
    sources: list[dict[str, Any]]

    # Tool
    tool_name: str | None
    tool_arguments: dict[str, Any]
    tool_result: Any
    tool_error: str | None

    # Final output
    final_answer: str

    # Debugging
    steps: list[str]
