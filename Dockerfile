
FROM python:3.11-slim

# Python 运行配置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HF_HOME=/home/appuser/.cache/huggingface

WORKDIR /app

# 安装部分机器学习依赖可能需要的系统库
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libgomp1 \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户和模型缓存目录
RUN useradd --create-home --shell /bin/sh appuser \
    && mkdir -p /home/appuser/.cache/huggingface \
    && chown -R appuser:appuser /home/appuser

# 优先复制依赖，利用 Docker 构建缓存
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --no-cache-dir \
    -r /app/requirements.txt

# 复制应用代码
COPY --chown=appuser:appuser src /app/src
COPY --chown=appuser:appuser scripts /app/scripts
COPY --chown=appuser:appuser alembic /app/alembic
COPY --chown=appuser:appuser alembic.ini /app/alembic.ini

# 创建数据目录
RUN mkdir -p /app/data \
    && chown -R appuser:appuser /app/data

# 避免以 root 权限运行应用
USER appuser

EXPOSE 8000

# API 容器默认启动命令
CMD ["uvicorn", "health_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
