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
from health_agent.core.config import (
    get_settings,
)
from health_agent.llm.provider import (
    LLMProvider,
)
from health_agent.mcp.client import (
    HealthMCPClient,
)
from health_agent.rag.factory import (
    build_rag_service,
)


@lru_cache
def build_agent_service() -> AgentService:
    settings = get_settings()

    llm = LLMProvider()

    rag_service = build_rag_service()

    mcp_client = HealthMCPClient(server_url=(settings.mcp_health_server_url))

    checkpointer = InMemorySaver()

    graph = build_agent_graph(
        llm=llm,
        rag_service=(rag_service),
        mcp_client=(mcp_client),
        checkpointer=(checkpointer),
    )

    return AgentService(graph=graph)
