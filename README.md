# AI 运维助手 — 生产级 FastAPI 项目骨架

一套按 DDD 分层思路组织的 FastAPI 项目骨架：接口层 / 应用层 / 领域模型 /
基础设施层职责分离，`services/` 里的业务逻辑不直接依赖具体的 LLM、embedding、
向量库实现，方便后续更换供应商或做单元测试。

## 目录结构

```
app/
├── main.py                 # FastAPI 实例 + lifespan 启动/关闭钩子
├── api/                    # 接口层：路由、依赖注入
├── core/                   # 全局配置、日志、异常处理
├── schemas/                # API 请求/响应的 Pydantic 模型（DTO）
├── models/                 # 数据库 ORM 模型
├── services/                # 业务逻辑（应用层）
├── repositories/           # 数据访问层（Repository 模式）
├── infrastructure/         # 外部依赖：LLM / embedding / 向量库 / MCP
├── db/                     # 数据库连接、session 管理
└── utils/                  # 通用工具

tests/
├── unit/                   # 纯业务逻辑测试，Mock 掉所有外部依赖
├── integration/            # 真实连数据库/向量库的集成测试
└── e2e/                    # 完整调一遍 API

alembic/                    # 数据库迁移
docker/                     # Dockerfile + docker-compose
scripts/                    # 开发辅助脚本（建表、灌数据）
```

## 快速开始

### 1. 准备环境变量

```bash
cp .env.example .env
# 按实际情况填写 DEEPSEEK_API_KEY、DATABASE_URL 等
```

### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

### 3. 准备依赖服务

这个项目假设以下服务已经在运行（可以复用你之前搭好的）：
- PostgreSQL（存会话/文档元数据）
- Redis（存短期会话记忆）
- 本地 TEI + BGE-M3 embedding 服务（`http://127.0.0.1:8001`）
- Milvus（向量库，`http://127.0.0.1:19530`）

没有 Postgres/Redis 的话，可以用 `docker/docker-compose.yml` 快速起：
```bash
docker compose -f docker/docker-compose.yml up -d postgres redis
```

### 4. 建表

```bash
python -m scripts.init_db
# 或用 alembic 管理迁移：
# alembic revision --autogenerate -m "init"
# alembic upgrade head
```

### 5.（可选）灌入示例知识库数据

```bash
python -m scripts.seed_data
```

### 6. 启动服务

```bash
uvicorn app.main:app --reload
```

打开 `http://127.0.0.1:8000/docs` 看接口文档。

### 7. 跑测试

```bash
pytest                          # 全部测试
pytest tests/unit                # 只跑单元测试（不依赖外部服务，最快）
pytest --cov=app tests/          # 带覆盖率
```
# 生成迁移
alembic revision --autogenerate -m "描述"
# 只看会执行什么 SQL，不真正执行
alembic upgrade head --sql
# 执行迁移到最新
alembic upgrade head
# 回滚一步
alembic downgrade -1
# 查看当前版本
alembic current
# 查看迁移历史
alembic history

## 设计要点

- **schemas 和 models 分离**：API 返回的字段不直接暴露数据库内部结构。
- **infrastructure 层做抽象接口**：`services/` 只依赖 `LLMClient` 这样的抽象，
  换供应商（比如从 DeepSeek 换成别的模型）只需要新增实现类。
- **配置用 pydantic-settings**：启动阶段就能发现配置缺失/类型错误，
  避免类似 `base_url` 读成 `None` 但运行时才报错的问题。
- **lifespan 管理外部连接**：向量库连接等资源统一在启动时初始化、关闭时释放。
- **单元测试 Mock 外部依赖**：`ChatService` 的编排逻辑可以完全脱离真实的
  LLM/数据库/向量库跑测试，测试速度快、也不受外部服务稳定性影响。

## 后续可以扩展的方向

- 把 `infrastructure/mcp/` 填充为 MCP Client 封装，让 Agent 能调用标准化的外部工具
- `services/` 里加混合检索（向量 + BM25）逻辑
- 加认证鉴权（`core/security.py` 目前是占位）
- 加 Prometheus 监控指标、结构化日志（JSON格式，方便日志采集）
