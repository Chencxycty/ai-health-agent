from typing import Any

from langgraph.types import interrupt

from health_agent.agent.risk import assess_risk
from health_agent.agent.state import AgentState
from health_agent.llm.provider import LLMProvider
from health_agent.llm.router import classify_intent
from health_agent.rag.service import RAGService
from health_agent.tools.registry import (
    TOOLS,
    execute_tool,
)
from health_agent.mcp.client import (
    HealthMCPClient,
)
from health_agent.observability.tracing import (
    get_tracer,
)
from opentelemetry.trace import (
    Status,
    StatusCode,
)


tracer = get_tracer()


class AgentNodes:
    def __init__(
        self,
        llm,
        rag_service,
        mcp_client: HealthMCPClient,
    ) -> None:
        self.llm = llm

        self.rag_service = rag_service

        self.mcp_client = mcp_client

    def risk_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        with tracer.start_as_current_span("agent.risk") as span:
            assessment = assess_risk(state["user_message"])

            span.set_attribute(
                "agent.risk_level",
                assessment.level,
            )

            span.set_attribute(
                "agent.review_required",
                assessment.level == "high",
            )

            return {
                "risk_level": assessment.level,
                "risk_reason": assessment.reason,
                "review_required": assessment.level == "high",
                "steps": [
                    *state.get(
                        "steps",
                        [],
                    ),
                    "risk_check",
                ],
            }

    def human_review_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        decision = interrupt(
            {
                "type": "high_risk_review",
                "message": state["user_message"],
                "reason": state.get(
                    "risk_reason",
                    "",
                ),
                "question": ("是否允许 Agent 继续生成普通健康信息处理流程？"),
            }
        )

        return {
            "review_approved": bool(decision),
            "steps": [
                *state.get("steps", []),
                "human_review",
            ],
        }

    def safe_answer_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        answer = (
            "该描述可能涉及需要及时处理的健康风险。"
            "当前系统不适合对此进行个体诊断或自行处置建议。"
            "如症状严重、突然出现或持续加重，"
            "应及时联系当地急救服务或前往医疗机构评估。"
        )

        return {
            "final_answer": answer,
            "messages": [
                {
                    "role": "assistant",
                    "content": answer,
                }
            ],
            "steps": [
                *state.get("steps", []),
                "safe_answer",
            ],
        }

    def router_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        with tracer.start_as_current_span("agent.router") as span:
            result = classify_intent(
                llm=self.llm,
                query=state["user_message"],
            )

            span.set_attribute(
                "agent.route",
                result.intent,
            )

            span.set_attribute(
                "agent.route_confidence",
                result.confidence,
            )

            return {
                "route": result.intent,
                "confidence": result.confidence,
                "steps": [
                    *state.get(
                        "steps",
                        [],
                    ),
                    "router",
                ],
            }

    def chat_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        history = self._build_history(state)

        response = self.llm.chat(
            system_prompt=(
                "你是一名友好的健康信息助手。"
                "普通聊天可以自然回答。"
                "不要进行个体医疗诊断。"
            ),
            user_prompt=(
                f"历史对话：\n{history}\n\n当前问题：\n{state['user_message']}"
            ),
            temperature=0.2,
        )

        answer = response.content

        return {
            "final_answer": answer,
            "messages": [
                {
                    "role": "assistant",
                    "content": answer,
                }
            ],
            "steps": [
                *state.get("steps", []),
                "chat",
            ],
        }

    def rag_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        with tracer.start_as_current_span("agent.rag") as span:
            query = state.get("rag_query") or state["user_message"]

            result = self.rag_service.answer(
                query=query,
                top_k=5,
            )

            sources = [
                {
                    "source_id": citation.source_id,
                    "title": citation.title,
                    "page": citation.page,
                    "chunk_id": citation.chunk_id,
                }
                for citation in result.citations
            ]

            span.set_attribute(
                "rag.source_count",
                len(sources),
            )

            span.set_attribute(
                "rag.retrieval_latency_ms",
                result.retrieval_latency_ms,
            )

            span.set_attribute(
                "rag.generation_latency_ms",
                result.generation_latency_ms,
            )

            if result.total_tokens is not None:
                span.set_attribute(
                    "llm.total_tokens",
                    result.total_tokens,
                )

            return {
                "final_answer": result.answer,
                "sources": sources,
                "messages": [
                    {
                        "role": "assistant",
                        "content": result.answer,
                    }
                ],
                "steps": [
                    *state.get(
                        "steps",
                        [],
                    ),
                    "rag",
                ],
            }

    def tool_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        with tracer.start_as_current_span("agent.mcp_tool") as span:
            try:
                tools = self.mcp_client.openai_tool_schemas()

                tool_call = self.llm.choose_tool(
                    user_prompt=(state["user_message"]),
                    tools=tools,
                )

                if tool_call is None:
                    span.set_attribute(
                        "tool.selected",
                        False,
                    )

                    return {
                        "tool_error": "No MCP tool selected.",
                        "steps": [
                            *state.get(
                                "steps",
                                [],
                            ),
                            "mcp_tool_selection_failed",
                        ],
                    }

                span.set_attribute(
                    "tool.selected",
                    True,
                )

                span.set_attribute(
                    "tool.name",
                    tool_call.name,
                )

                result = self.mcp_client.call_tool(
                    name=tool_call.name,
                    arguments=(tool_call.arguments),
                )

                span.set_attribute(
                    "tool.success",
                    not result.is_error,
                )

                return {
                    "tool_name": tool_call.name,
                    "tool_arguments": tool_call.arguments,
                    "tool_result": result.data,
                    "tool_error": result.error,
                    "steps": [
                        *state.get(
                            "steps",
                            [],
                        ),
                        f"mcp_tool:{tool_call.name}",
                    ],
                }

            except Exception as exc:
                # 1. 把异常记录到当前 Span
                span.record_exception(exc)

                # 2. 明确告诉 OpenTelemetry：
                #    这个 Span 是失败状态
                span.set_status(
                    Status(
                        StatusCode.ERROR,
                        str(exc),
                    )
                )

                # 3. 也可以额外记录一些安全的属性
                span.set_attribute(
                    "tool.success",
                    False,
                )

                span.set_attribute(
                    "error.type",
                    type(exc).__name__,
                )

                return {
                    "tool_error": str(exc),
                    "steps": [
                        *state.get(
                            "steps",
                            [],
                        ),
                        "mcp_tool_exception",
                    ],
                }

    def tool_answer_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        if state.get("tool_error"):
            answer = f"当前无法完成该健康计算。原因：{state['tool_error']}"

        else:
            response = self.llm.chat(
                system_prompt=(
                    "你是一名健康信息助手。"
                    "工具结果是确定性计算结果。"
                    "请基于结果进行简洁说明，"
                    "不要重新计算，"
                    "不要进行医学诊断。"
                ),
                user_prompt=(
                    f"用户问题："
                    f"{state['user_message']}\n"
                    f"工具："
                    f"{state.get('tool_name')}\n"
                    f"参数："
                    f"{state.get('tool_arguments')}\n"
                    f"结果："
                    f"{state.get('tool_result')}"
                ),
                temperature=0.1,
            )

            answer = response.content

        return {
            "final_answer": answer,
            "messages": [
                {
                    "role": "assistant",
                    "content": answer,
                }
            ],
            "steps": [
                *state.get("steps", []),
                "tool_answer",
            ],
        }

    def _build_history(
        self,
        state: AgentState,
    ) -> str:
        messages = state.get(
            "messages",
            [],
        )

        recent_messages = messages[-8:]

        return "\n".join(
            f"{message['role']}: {message['content']}" for message in recent_messages
        )

    def prepare_turn_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        return {
            "route": "unclassified",
            "confidence": 0.0,
            "risk_level": "unknown",
            "risk_reason": "",
            "review_required": False,
            "review_approved": False,
            "tool_name": None,
            "tool_arguments": {},
            "tool_result": None,
            "tool_error": None,
            "rag_query": "",
            "sources": [],
            "final_answer": "",
            "steps": ["prepare_turn"],
        }

    # def rewrite_query_node(
    #     self,
    #     state: AgentState,
    # ) -> dict[str, Any]:
    #     messages = state.get(
    #         "messages",
    #         [],
    #     )

    #     recent_history = messages[-6:]

    #     history_text = "\n".join(
    #         f"{message['role']}: {message['content']}" for message in recent_history
    #     )

    #     response = self.llm.chat(
    #         system_prompt=(
    #             "你负责将多轮对话中的当前问题"
    #             "改写成适合知识库检索的独立问题。"
    #             "只做必要的指代消解，"
    #             "不得引入对话中不存在的新医学事实。"
    #             "只返回改写后的问题。"
    #         ),
    #         user_prompt=(
    #             f"历史对话：\n{history_text}\n\n当前问题：\n{state['user_message']}"
    #         ),
    #         temperature=0.0,
    #     )

    #     rewritten = response.content.strip()

    #     return {
    #         "rag_query": rewritten,
    #         "steps": [
    #             *state.get(
    #                 "steps",
    #                 [],
    #             ),
    #             "rewrite_query",
    #         ],
    #     }
    def rewrite_query_node(
        self,
        state: AgentState,
    ) -> dict[str, Any]:
        with tracer.start_as_current_span("agent.query_rewrite") as span:
            messages = state.get(
                "messages",
                [],
            )

            recent_history = messages[-6:]

            history_text = "\n".join(
                f"{message['role']}: {message['content']}" for message in recent_history
            )

            response = self.llm.chat(
                system_prompt=(
                    "你负责将多轮对话中的当前问题"
                    "改写成适合知识库检索的独立问题。"
                    "只做必要的指代消解，"
                    "不得引入对话中不存在的新医学事实。"
                    "只返回改写后的问题。"
                ),
                user_prompt=(
                    f"历史对话：\n{history_text}\n\n当前问题：\n{state['user_message']}"
                ),
                temperature=0.0,
            )

            rewritten = response.content.strip()

            span.set_attribute(
                "rewrite.performed",
                True,
            )

            return {
                "rag_query": rewritten,
                "steps": [
                    *state.get(
                        "steps",
                        [],
                    ),
                    "rewrite_query",
                ],
            }
