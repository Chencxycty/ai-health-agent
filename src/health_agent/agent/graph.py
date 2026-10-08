from typing import Literal

from langgraph.checkpoint.memory import (
    InMemorySaver,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from health_agent.agent.nodes import AgentNodes
from health_agent.agent.state import AgentState
from health_agent.llm.provider import (
    LLMProvider,
)
from health_agent.rag.service import (
    RAGService,
)


def route_after_risk(
    state: AgentState,
) -> Literal[
    "human_review",
    "router",
]:
    if state.get("risk_level") == "high":
        return "human_review"

    return "router"


def route_after_review(
    state: AgentState,
) -> Literal[
    "router",
    "safe_answer",
]:
    if state.get(
        "review_approved",
        False,
    ):
        return "router"

    return "safe_answer"


def route_after_router(
    state: AgentState,
) -> Literal[
    "rewrite_query",
    "tool",
    "chat",
]:
    route = state.get("route")

    if route == "medical_knowledge":
        return "rewrite_query"

    if route == "health_calculation":
        return "tool"

    return "chat"


def build_agent_graph(
    llm,
    rag_service,
    mcp_client,
    checkpointer=None,
):
    nodes = AgentNodes(
        llm=llm,
        rag_service=(rag_service),
        mcp_client=(mcp_client),
    )

    builder = StateGraph(AgentState)

    builder.add_node(
        "risk",
        nodes.risk_node,
    )

    builder.add_node(
        "human_review",
        nodes.human_review_node,
    )

    builder.add_node(
        "safe_answer",
        nodes.safe_answer_node,
    )

    builder.add_node(
        "router",
        nodes.router_node,
    )

    builder.add_node(
        "chat",
        nodes.chat_node,
    )

    builder.add_node(
        "rag",
        nodes.rag_node,
    )

    builder.add_node(
        "prepare_turn",
        nodes.prepare_turn_node,
    )

    builder.add_edge(
        START,
        "prepare_turn",
    )

    builder.add_edge(
        "prepare_turn",
        "risk",
    )

    builder.add_node(
        "rewrite_query",
        nodes.rewrite_query_node,
    )

    builder.add_edge(
        "rewrite_query",
        "rag",
    )

    builder.add_node(
        "tool",
        nodes.tool_node,
    )

    builder.add_node(
        "tool_answer",
        nodes.tool_answer_node,
    )

    # builder.add_edge(
    #     START,
    #     "risk",
    # )

    builder.add_conditional_edges(
        "risk",
        route_after_risk,
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_review,
    )

    builder.add_conditional_edges(
        "router",
        route_after_router,
    )

    builder.add_edge(
        "chat",
        END,
    )

    builder.add_edge(
        "rag",
        END,
    )

    builder.add_edge(
        "tool",
        "tool_answer",
    )

    builder.add_edge(
        "tool_answer",
        END,
    )

    builder.add_edge(
        "safe_answer",
        END,
    )

    if checkpointer is None:
        checkpointer = InMemorySaver()

    return builder.compile(checkpointer=checkpointer)
