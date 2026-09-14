FROM python:3.11-slim AS base

WORKDIR /app

# 系统依赖（asyncpg等编译需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000

# 生产环境用多worker，本地调试可以加 --reload 单独覆盖
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
