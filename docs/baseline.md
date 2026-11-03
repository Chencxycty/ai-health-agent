# Day 22 基线、回归集与数据库升级

## 当日实现范围

Day 22 固定四项基础设施：接口与会话契约、七类固定回归用例、可重复的机器可读基线、Alembic 业务表迁移。Checkpoint 持久化、重复恢复防护和跨重启恢复留到 Day 23。

固定回归集位于 `data/eval/week4_regression.json`，覆盖普通对话、医疗 RAG、BMI/MCP、合成患者数据、多轮会话、人工介入及非法输入。基线工具逐条保留状态、耗时、观测摘要与失败原因，并计算 P50/P95；失败用例不会被总分掩盖。

## 固定环境

- Python：3.11（当前开发环境为 3.11.16）。
- 依赖：`requirements.txt` 中使用精确版本；Alembic 固定为 1.20.1。
- 应用镜像：`ai-health-agent:0.3.0`；数据库镜像：`pgvector/pgvector:pg17`。
- 模型：从 `LLM_MODEL` 读取并写入报告，不记录 API 密钥。
- 硬件：报告记录操作系统、架构、处理器、逻辑 CPU 数和 `CUDA_VISIBLE_DEVICES`。

## 空数据库初始化

先启动 PostgreSQL，再执行：

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m alembic upgrade head
python scripts/seed_patient_data.py
python scripts/ingest_db.py
```

初始迁移首先执行 `CREATE EXTENSION IF NOT EXISTS vector`，然后才创建 `embedding VECTOR(1024)`。Alembic 只管理 `document_chunks`、`patients`、`observations` 和 `conditions`；LangGraph checkpoint 表由对应 SDK 管理，不在自动生成范围内。

`scripts/init_db.py` 已改为调用 `alembic upgrade head`，不再使用 `metadata.create_all()` 绕过版本历史。

## 已有 v0.3.0 数据库升级

先备份，示例：

```powershell
pg_dump --format=custom --file=health_agent_v030.backup $env:DATABASE_URL
```

之后只读比对真实结构：

```powershell
python scripts/validate_v030_schema.py `
  --report reports/week4/v030-schema-validation.json
```

只有报告同时满足 `vector_extension_installed=true`、`schema_matches=true`，才允许登记初始版本：

```powershell
python scripts/validate_v030_schema.py --stamp `
  --report reports/week4/v030-stamp.json
```

`--stamp` 会在结构完全一致时执行 `alembic stamp head`，并比较登记前后的四张业务表行数。只要存在字段、索引、外键或类型差异，脚本就以非零状态退出且不会 stamp。不要通过删除数据卷或盲目执行 `alembic stamp` 消除差异。

## 采集功能与性能基线

在数据库迁移、演示数据导入、MCP 与 API 均已启动后运行：

```powershell
python scripts/capture_day22_baseline.py
```

默认输出 `reports/week4/baseline.json`。该脚本会产生少量真实模型调用，因此不放入每次提交都运行的快速测试。报告里的性能数字只描述本次固定环境和小样本，不代表稳定容量。

快速、无需真实模型的契约与迁移验证：

```powershell
pytest -q tests/test_day22_contract.py tests/test_day22_migrations.py
python -m alembic upgrade head --sql
```

## 验收判定

- API 字段、`thread_id` 规则、引用、工具与人工介入语义有文档和自动化测试约束。
- 空库迁移生成四张业务表，pgvector 扩展创建顺序正确。
- 旧库只有在结构一致时才能登记基线，登记前后行数一致。
- 基线报告包含逐用例结果、失败原因、P50/P95、模型和运行环境。
- 原有患者与知识库数据能在迁移后查询；真实结果须以生成的 schema validation 和 baseline 报告为证，不能用本文替代执行记录。
