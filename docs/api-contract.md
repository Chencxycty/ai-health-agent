# API 契约（Day 22 基线）

本文冻结 v0.3.0 在 Day 22 核对后的真实 HTTP 契约。后续修改字段、状态码或会话语义时，必须同步更新本文和 `tests/test_day22_contract.py`。

## 会话标识规则

- `thread_id` 由调用方生成并持久保存，长度为 1～200 个字符；建议使用 UUID 或“业务前缀 + UUID”。
- 同一段多轮会话的所有 `/agent/query` 请求必须复用同一个 `thread_id`，不同会话必须使用不同值。
- `/agent/resume` 只能使用产生人工中断时的原 `thread_id`，不能创建新会话，也不能用 `patient_id` 代替。
- 当前响应不回显 `thread_id`，因此调用方必须在发起请求前保存它。
- `thread_id` 只是状态分区键，不代表用户身份或患者数据访问授权。

## `POST /agent/query`

请求：

```json
{
  "message": "什么是高血压？",
  "thread_id": "conversation-550e8400-e29b-41d4-a716-446655440000"
}
```

`message` 长度为 1～5000，`thread_id` 长度为 1～200。成功响应：

```json
{
  "answer": "……",
  "route": "medical_knowledge",
  "tool_name": null,
  "sources": [
    {
      "source_id": 1,
      "title": "高血压指南",
      "page": 10,
      "chunk_id": "chunk-001"
    }
  ],
  "steps": ["prepare_turn", "risk_check", "router", "rewrite_query", "rag"],
  "interrupted": false,
  "interrupt_payload": null
}
```

字段约定：

- `route` 为 `unclassified`、`medical_knowledge`、`health_calculation` 或 `general_chat`。
- `sources` 只包含实际检索到的引用；无证据时为空数组，不能伪造引用。
- `tool_name` 是本轮最终选中的 MCP 工具名称；未调用工具时为 `null`。
- 工具原始结果保存在 Agent 内部状态的 `tool_result`，对外通过 `answer` 表达，当前契约不直接暴露原始工具结果。
- `steps` 用于调试流程，不应作为最终用户文案。

## 人工介入和 `POST /agent/resume`

高风险输入会返回 HTTP 200，但 `interrupted=true`。此时 `answer` 通常为空，`interrupt_payload` 包含：

```json
{
  "type": "high_risk_review",
  "message": "原始输入",
  "reason": "命中的风险原因",
  "question": "是否允许 Agent 继续……"
}
```

恢复请求：

```json
{
  "thread_id": "产生中断的原会话 ID",
  "approved": false
}
```

响应结构与 `/agent/query` 相同。`approved=false` 进入安全回答；`approved=true` 才继续普通路由。重复恢复和“会话并未处于中断状态”的校验属于 Day 23 持久化恢复工作，Day 22 不宣称已经支持。

## 其他现有端点

- `GET /health`：返回 `{"status":"ok"}`。
- `POST /chat`：请求字段 `message`，返回回答、模型名和 token 统计。
- `POST /rag/query`：请求字段 `query`、`top_k`，返回回答、结构化引用、token 与分阶段耗时。

## 错误语义

- Pydantic 输入校验失败：HTTP 422。
- 模型超时：HTTP 504，`error=llm_timeout`。
- 模型限流：HTTP 429，`error=llm_rate_limit`。
- 模型连接失败：HTTP 503，`error=llm_connection_error`。
- 其他模型服务错误：HTTP 502，`error=llm_provider_error`。

API 目前是本地单 worker 演示边界，没有实现真实身份认证；客户端传入的 `thread_id` 和 `patient_id` 均不能构成授权依据。
