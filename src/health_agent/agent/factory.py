from functools import lru_cache

from langgraph.checkpoint.memory import (
    InMemorySaver,
)

from health_agent.agent.graph import (
    build_agent_graph,
)
from health_agent.agent.service import (
    AgentService,
)
from health_agent.llm.provider import (
    LLMProvider,
)
from health_agent.rag.factory import (
    build_rag_service,
)


@lru_cache
def build_agent_service() -> AgentService:
    llm = LLMProvider()

    rag_service = build_rag_service()

    checkpointer = InMemorySaver()

    graph = build_agent_graph(
        llm=llm,
        rag_service=rag_service,
        checkpointer=checkpointer,
    )

    return AgentService(graph=graph)
