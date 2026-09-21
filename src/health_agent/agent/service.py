from dataclasses import dataclass
from typing import Any

from langgraph.types import Command


@dataclass(frozen=True)
class AgentRunResult:
    answer: str

    route: str

    rag_query: str

    tool_name: str | None

    sources: list[dict[str, Any]]

    steps: list[str]

    interrupted: bool

    interrupt_payload: Any | None


class AgentService:
    def __init__(
        self,
        graph,
    ) -> None:
        self.graph = graph

    def query(
        self,
        message: str,
        thread_id: str,
    ) -> AgentRunResult:
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        result = self.graph.invoke(
            {
                "user_message": message,
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
            },
            config=config,
        )

        return self._to_result(result)

    def resume(
        self,
        thread_id: str,
        approved: bool,
    ) -> AgentRunResult:
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        result = self.graph.invoke(
            Command(resume=approved),
            config=config,
        )

        return self._to_result(result)

    def get_state(
        self,
        thread_id: str,
    ):
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        return self.graph.get_state(config)

    @staticmethod
    def _to_result(
        state,
    ) -> AgentRunResult:
        interrupts = state.get(
            "__interrupt__",
            (),
        )

        interrupted = bool(interrupts)

        payload = None

        if interrupted:
            payload = interrupts[0].value

        return AgentRunResult(
            answer=state.get(
                "final_answer",
                "",
            ),
            route=state.get(
                "route",
                "unclassified",
            ),
            rag_query=state.get(
                "rag_query",
                "",
            ),
            tool_name=state.get(
                "tool_name",
            ),
            sources=state.get(
                "sources",
                [],
            ),
            steps=state.get(
                "steps",
                [],
            ),
            interrupted=interrupted,
            interrupt_payload=payload,
        )
