# AI Health Agent（学习自用，非完整Agent项目）

> v0.3.0 · 基于 FastAPI、LangGraph、RAG、MCP 与 PostgreSQL/pgvector 的健康信息智能体后端。

AI Health Agent 是一个面向学习、验证和原型开发的健康信息助手。项目将普通对话、医学知识检索、确定性健康计算、风险识别与人工审核组织到统一的 Agent 工作流中，并提供 FastAPI、MCP、FHIR 数据转换、OpenTelemetry 可观测性和 Docker Compose 部署能力。

> [!IMPORTANT]
> 本项目不提供医疗诊断、处方或急救决策，不能替代医生。遇到严重、突发或持续加重的症状，请及时联系当地急救服务或前往医疗机构。

## 功能概览

- **Agent 编排**：使用 LangGraph 组织风险检查、意图路由、查询改写、RAG、MCP 工具调用和回答生成。
- **三类请求路由**：支持 `medical_knowledge`、`health_calculation` 与 `general_chat`。
- **混合 RAG**：结合 PostgreSQL/pgvector 向量检索、BM25、RRF 融合与交叉编码器重排，并返回结构化引用。
- **风险与人工介入**：命中高风险模式时中断工作流，可通过 `/agent/resume` 审核后继续或转入安全回答。
- **MCP 健康工具**：提供 BMI、平均血压、平均血糖及合成/去标识患者摘要工具。
- **健康数据与 FHIR**：管理患者、观察指标和健康状况，并可转换为 FHIR Bundle。
- **可观测性**：使用 OpenTelemetry 记录 Agent、RAG、MCP 和 FastAPI 调用链路。
- **工程化支持**：包含 Alembic 迁移、Docker Compose、回归数据集、评估脚本和自动化测试。

## 系统架构

```mermaid
flowchart LR
    Client[客户端] --> API[FastAPI]
    API --> Agent[LangGraph Agent]
    Agent --> Risk{风险检查}
    Risk -->|高风险| HITL[人工审核]
    Risk -->|普通| Router{意图路由}
    HITL --> Router
    HITL --> Safe[安全回答]
    Router -->|医学知识| RAG[Hybrid RAG]
    Router -->|健康计算| MCP[MCP Server]
    Router -->|普通对话| LLM[LLM Provider]
    RAG --> PG[(PostgreSQL + pgvector)]
    RAG --> LLM
    MCP --> Tools[健康计算 / 患者摘要]
    Tools --> PG
```

Agent 的主流程为：

```text
prepare_turn -> risk -> human_review? -> router
  -> medical_knowledge -> rewrite_query -> rag
  -> health_calculation -> mcp_tool -> tool_answer
  -> general_chat -> chat
```

## 技术栈

- Python 3.11
- FastAPI + Uvicorn
- LangGraph + LangChain Core
- OpenAI 兼容的 LLM API
- BAAI/bge-m3 + BAAI/bge-reranker-v2-m3
- PostgreSQL 17 + pgvector + SQLAlchemy + Alembic
- Model Context Protocol (MCP)
- OpenTelemetry
- Docker + Docker Compose
- Pytest + Ruff

## 项目结构

```text
.
├── alembic/                         # 数据库迁移
├── data/
│   ├── eval/                        # 检索、RAG、Agent 回归数据集
│   └── processed/                   # 已切分文本与向量
├── docs/                            # API 契约与基线说明
├── reports/                         # 验证/评估报告
├── scripts/                         # 初始化、导入、演示、评估脚本
├── src/health_agent/
│   ├── agent/                       # LangGraph 状态、节点和工作流
│   ├── api/                         # FastAPI 接口
│   ├── core/                        # 配置与日志
│   ├── database/                    # 数据模型与仓储
│   ├── healthcare/                  # 患者数据与 FHIR
│   ├── llm/                         # 模型调用与意图路由
│   ├── mcp/                         # MCP 客户端和服务端
│   ├── observability/               # OpenTelemetry
│   ├── rag/                         # 切分、检索、融合、重排与生成
│   └── tools/                       # 确定性健康计算
└── tests/                           # 单元测试与契约测试
```

## 快速开始（Docker Compose）

### 1. 准备配置

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，至少填写：

```dotenv
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
LLM_MODEL=your-model-name
DATABASE_URL=postgresql+psycopg://health:health@localhost:5432/health_agent
```

`.env` 已被 `.gitignore` 排除，请勿提交任何真实密钥。

### 2. 启动服务

```powershell
docker compose up --build -d
docker compose ps
```

Compose 会启动：

| 服务 | 地址 | 说明 |
| --- | --- | --- |
| API | `http://127.0.0.1:8000` | FastAPI 与 Agent 接口 |
| Swagger UI | `http://127.0.0.1:8000/docs` | 交互式 API 文档 |
| MCP | `http://127.0.0.1:8100/mcp` | Streamable HTTP MCP 服务 |
| PostgreSQL | `127.0.0.1:5432` | pgvector 数据库 |

### 3. 初始化数据库与演示数据

```powershell
docker compose exec api python -m alembic upgrade head
docker compose exec api python scripts/seed_patient_data.py
docker compose exec api python scripts/ingest_db.py
```

`ingest_db.py` 会将 `data/processed/chunks.json` 和 `data/processed/embeddings.npy` 导入空数据库，请勿对同一批数据重复执行。

### 4. 验证服务

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
python scripts/smoke_test.py
python scripts/smoke_test.py --full
```

首次执行 RAG 时可能需要下载嵌入与重排模型，启动时间取决于网络和本地缓存。

停止服务：

```powershell
docker compose down
```

如需同时删除本地数据库卷和模型缓存卷，可执行 `docker compose down -v`；该操作会删除本地持久化数据。

## 本地开发

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH = "$PWD\src"
```

先启动数据库并执行迁移：

```powershell
docker compose up -d postgres
python -m alembic upgrade head
python scripts/seed_patient_data.py
python scripts/ingest_db.py
```

在两个终端中分别启动 MCP 与 API：

```powershell
# 终端 1
$env:PYTHONPATH = "$PWD\src"
python -m health_agent.mcp.server --transport streamable-http --host 127.0.0.1 --port 8100
```

```powershell
# 终端 2
$env:PYTHONPATH = "$PWD\src"
uvicorn health_agent.api.main:app --reload --host 127.0.0.1 --port 8000
```

## API 示例

### 健康检查

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### Agent 查询

`thread_id` 由调用方生成并保存；同一段多轮会话必须复用同一个值。

```powershell
$body = @{
  message   = "什么是高血压？"
  thread_id = "demo-conversation-001"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/agent/query `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

典型响应包含：

```json
{
  "answer": "...",
  "route": "medical_knowledge",
  "tool_name": null,
  "sources": [],
  "steps": ["prepare_turn", "risk_check", "router", "rewrite_query", "rag"],
  "interrupted": false,
  "interrupt_payload": null
}
```

### 恢复人工审核流程

当 `/agent/query` 返回 `interrupted: true` 时，可使用原 `thread_id` 恢复：

```powershell
$body = @{
  thread_id = "demo-conversation-001"
  approved  = $false
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/agent/resume `
  -Method Post `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

更多字段约定见 [`docs/api-contract.md`](docs/api-contract.md)。

## MCP 工具

MCP 服务当前注册以下工具：

| 工具 | 用途 |
| --- | --- |
| `calculate_bmi` | 根据身高和体重计算 BMI |
| `calculate_average_blood_pressure` | 计算多次收缩压/舒张压的平均值 |
| `calculate_average_glucose` | 计算多次血糖值的算术平均值 |
| `get_patient_summary` | 查询合成或去标识患者摘要 |

计算工具只返回确定性结果，不执行医学诊断。患者数据工具也不包含身份认证或授权逻辑，不应直接用于生产环境。

## 测试与质量检查

```powershell
# 全量测试
python -m pytest -q

# v0.3.0 契约与数据库迁移测试
python -m pytest -q tests/test_day22_contract.py tests/test_day22_migrations.py

# 静态检查
ruff check src tests scripts
```

评估脚本：

```powershell
python scripts/evaluate_retrieval.py
python scripts/evaluate_rag.py
python scripts/evaluate_agent.py
python scripts/capture_day22_baseline.py
```

真实模型评估可能产生 API 调用费用。数据库迁移、基线与旧库校验说明见 [`docs/baseline.md`](docs/baseline.md)。

## v0.3.0 主要内容

- 新增 LangGraph Agent、意图路由、多轮会话状态与高风险人工审核。
- 新增混合检索、查询改写、结构化引用与检索/生成耗时统计。
- 新增 MCP 客户端与服务端，接入健康计算和患者摘要工具。
- 新增患者、观察指标、健康状况模型及 FHIR 转换能力。
- 新增 PostgreSQL/pgvector 持久化与 Alembic 业务表迁移。
- 新增 OpenTelemetry 链路追踪、Docker 镜像及 Compose 编排。
- 新增契约、回归、迁移、RAG、Agent、MCP 与可观测性测试。

## 已知限制

- 目前是本地/原型后端，没有身份认证、患者访问授权、限流和生产级隐私保护。
- LangGraph 默认使用内存检查点；进程重启后会话状态不会保留。
- 高风险检测主要基于关键词规则，不应视为临床分诊系统。
- RAG 的可靠性取决于导入文档、嵌入模型、重排模型和评估数据质量。
- FHIR 输出用于数据映射演示，不代表已通过完整的 FHIR 一致性验证。

## 安全与隐私

- 仅使用合成或经过充分去标识的数据进行开发和演示。
- 不要将 `.env`、API 密钥、真实患者数据、数据库备份或敏感运行日志提交到 Git。
- 对外部署前应补充身份认证、细粒度授权、审计、加密、密钥管理、数据保留策略和合规评审。

## License

仓库当前尚未提供开源许可证。若计划公开发布，请先选择并添加合适的 `LICENSE` 文件；在此之前，默认不授予他人复制、修改或分发本项目的权利。
