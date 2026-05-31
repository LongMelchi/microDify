# microDify — Agent 开发蓝图

> 本文件是给 **AI Agent** 的执行规范；产品愿景见 `docs/vision.md`，人类向的架构图谱见 `docs/microDify-map.md`。
> **项目状态：🟢 全新项目 —— 下述全部为目标设计，代码尚未实现，按本蓝图从零搭建。**
> **图例：🔴 红线（必须遵守，拿不准先停下确认）｜⚪ 背景（参考）｜⏳ 待搭建**

microDify 是 Dify 的简化版 AI Agent 平台：模块化单体，Docker Compose 本地部署，面向团队内部 20-50 人，单人开发维护。**核心原则：只做高价值功能，砍掉一切不必要的复杂度。**

## 1. 技术栈 ⚪

```
前端：React + Next.js (App Router) + TypeScript
后端：Python + FastAPI + uvicorn (2 workers)
数据库：PostgreSQL 16 + pgvector（向量检索 + 业务数据一套搞定）
缓存/队列：Redis（限流 + 文档异步处理 + 工作流状态）
反向代理：Caddy（HTTPS 终端 + 静态资源）
LLM SDK：openai + anthropic（统一抽象接口）
迁移：Alembic ｜ 容器化：Docker Compose
```

## 2. 模块架构与边界 🔴

### 目录结构

```
microDify/
├── app/                  # FastAPI 后端
│   ├── main.py           # 应用组装 & 生命周期
│   ├── core/             # 配置、数据库、安全、异常、分页、日志
│   ├── common/           # 文件存储、Redis 队列、限流、事件总线
│   ├── provider/         # OpenAI + Anthropic 适配，统一 LLMGateway
│   ├── auth/             # JWT + 账号密码
│   ├── agent/            # ReAct 推理 + 工具调用 + 知识库绑定
│   ├── chat/             # SSE 流式对话
│   ├── knowledge/        # 文档上传、解析、分块
│   ├── rag/              # pgvector 混合检索、Rerank
│   ├── workflow/         # 可视化编排、线性执行
│   └── prompt/           # 模板管理、变量插值
├── frontend/             # React + Next.js（app/ components/ hooks/ lib/ types/）
└── tests/                # 按模块组织的测试
```

### 模块职责（每个模块该建什么）

| 模块 | 职责 |
|------|------|
| `provider` | OpenAI/Anthropic 适配 + 统一 LLMGateway（含嵌入），预留扩展 Adapter |
| `auth` | JWT 无状态认证 + 账号密码校验 |
| `prompt` | 模板管理 + `{{variable}}` 变量插值 |
| `knowledge` | PDF/DOCX/TXT/MD/CSV 上传、解析、语义分块、向量化 |
| `rag` | pgvector 存储 + BM25/向量混合检索 + 简单 Rerank |
| `chat` | SSE 流式对话：绑定 Prompt 模板 + 可选关联知识库 |
| `agent` | ReAct 推理循环 + 动态工具调用 + 知识库绑定，SSE 流式返回推理过程 |
| `workflow` | 可视化编排，线性串联 + if/else 分支，5-6 种节点（开始/LLM/知识检索/条件/变量转换/结束） |

### 依赖白名单 🔴（不在表上 = 禁止 import）

| 模块 | 允许 import |
|------|-------------|
| `core/` | 无 |
| `common/` | `core` |
| `provider/` | `core` |
| `auth/` | `core` |
| `prompt/` | `core`, `auth` |
| `rag/` | `core`, `provider` |
| `knowledge/` | `core`, `common`, `auth`, `provider` |
| `chat/` | `core`, `auth`, `provider`, `rag`, `prompt` |
| `agent/` | `core`, `auth`, `provider`, `rag`, `prompt` |
| `workflow/` | `core`, `auth`, `provider`, `rag`, `prompt` |

依赖方向严格自上而下（`core` ← `common`/`provider`/`auth` ← `knowledge`/`rag`/`prompt` ← `agent`/`chat`/`workflow`）。`frontend/` 不参与后端依赖图，仅通过 HTTP 调后端。

### 跨模块规则 🔴

- 只 import 目标模块 `__init__.py` 暴露的公开符号。
- 跨模块只传 **ID / 原始值**（str / UUID / dict），不传 ORM 对象、不 import 对方 ORM/schemas/专项文件。
- 业务模块间禁止横向 import（如 `agent/` 不能 import `chat/`）。需要别的模块数据时，传 ID 在自己 service 里查。

## 3. 代码组织规范 🔴

> 以 Google Python/TypeScript 规范为基础，面向 AI 工具直接执行。

### 每个模块必含文件

| 文件 | 允许 | 不允许 |
|------|------|--------|
| `__init__.py` | 只 export router + 对外公开的 service 函数 | export 内部实现 |
| `router.py` | 声明路径/方法、注入 `Depends`、调 service 并返回 | DB 查询、ORM、业务逻辑、调外部 API |
| `models.py` | Column / relationship / ForeignKey / `__tablename__` | 业务方法、验证逻辑、API 调用 |
| `schemas.py` | Pydantic BaseModel + Field 约束（三种后缀） | DB 查询、调 service |
| `service.py` | async 业务逻辑、调同模块专项文件、调他模块公开接口、调 common | 接收 Request/Response/BackgroundTasks |
| `core/deps.py` | token 校验、DB session、Redis 连接 | 资源权限判断（放 service） |

### 允许的专项文件（`service.py` 超 400 行时拆，仅同模块可见）

`chunker.py`（文本算法）｜`parser.py`（文档解析）｜`executor.py`（核心执行 >100 行）｜`engine.py`（编排/调度）｜`nodes/`（多节点实现）｜`tools/`（多工具实现）

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块目录 | 小写单数 | `agent/` |
| Python 文件 | snake_case | `llm_node.py` |
| ORM Model | PascalCase 单数 | `ChatApp` |
| 表名 | snake_case 复数 | `chat_apps` |
| Pydantic Schema | `XxxCreate` / `XxxResponse` / `XxxFilter` | `ChatAppCreate` |
| Router/Service 函数 | 动词_名词 | `send_message` |

### 文件规模硬上限

`router.py` 150 行（超 → 拆子路由）｜`service.py` 400 行（超 → 提专项文件）｜`models.py` 100 行（超 → 评估拆模块）｜`schemas.py` 100 行（超 → 拆 `schemas/`）｜专项文件 300 行（超 → 继续拆）

### 新增模块流程

1. 用白名单校验依赖合规 → 2. 建 `app/<module>/` → 3. 建 4 个必含文件 → 4. `__init__.py` 只 export router + 公开 service → 5. `router.py` 用 `APIRouter(prefix="/<module>", tags=["<module>"])` → 6. `models.py` 继承 `Base`，`__tablename__="<module>s"` → 7. `schemas.py` 三后缀命名 → 8. `service.py` 纯 async，签名只收 db/user/业务参数 → 9. `main.py` 注册路由 → 10. 更新本文件白名单 → 11. 生成 Alembic 迁移

### import 自检（写 `from app.xxx import` 前）

目标在白名单内？→ 在 import ORM 模型？（跨模块就停，改传 ID）→ 在 import 别的业务模块？（停）→ 在 import 专项文件？（跨模块就停）→ 全过则确保 import 的是 `__init__.py` 暴露符号。

## 4. 数据模型 🔴

16 张表：10 张业务表 + 4 张执行记录表 + 2 张多对多关联表。预定义工具不建表，存为 `agents.enabled_tools` JSON 列（工具名数组）。

**业务表**

| 模块 | 表名 | 说明 |
|------|------|------|
| `auth/` | `users` | 用户，所有资源的归属点 |
| `prompt/` | `prompt_templates` | Prompt 模板，含 `{{variable}}` 占位符 |
| `knowledge/` | `knowledge_bases` | 知识库 |
| | `documents` | 上传的文档，归属一个知识库 |
| | `chunks` | 文档分块，含 embedding 向量，归属一个文档 |
| `chat/` | `chat_apps` | 对话应用，绑定 Prompt 模板 + 可选关联知识库 |
| | `conversations` | 一次对话会话，归属一个对话应用 |
| | `messages` | 会话中的一条消息，归属一个会话 |
| `agent/` | `agents` | Agent 配置：系统指令、模型选择、`enabled_tools` JSON、知识库绑定 |
| `workflow/` | `workflows` | 工作流定义 |

**执行记录表**

| 模块 | 表名 | 说明 |
|------|------|------|
| `agent/` | `agent_executions` | Agent 执行记录（输入、输出、ReAct 步骤 JSON、状态） |
| `workflow/` | `workflow_nodes` | 工作流节点（类型、配置 JSON） |
| | `workflow_edges` | 节点间连线（源、目标、条件表达式） |
| | `workflow_executions` | 工作流执行记录（输入、输出、各节点结果 JSON、状态） |

**关联表（多对多）**

| 表名 | 关联 |
|------|------|
| `chat_app_knowledge_bases` | chat_apps ↔ knowledge_bases |
| `agent_knowledge_bases` | agents ↔ knowledge_bases |

**不产生独立数据表的模块**：`core/`（基础设施）、`common/`（工具层）、`provider/`（配置走环境变量）、`rag/`（直接操作 chunks 的 embedding 列）

**核心关系链**

```
users
  ├── prompt_templates
  ├── knowledge_bases → documents → chunks (vector)
  ├── chat_apps → conversations → messages
  │     ├── (M:N) knowledge_bases
  │     └── (N:1) prompt_templates
  ├── agents → agent_executions
  │     ├── (M:N) knowledge_bases
  │     ├── (JSON) enabled_tools  # 预定义工具名数组，不建表
  │     └── (N:1) prompt_templates
  └── workflows → workflow_nodes + workflow_edges + workflow_executions
```

### 数据库性能规范

> AI 建表时直接执行。

**索引设计原则**

任何新表必须包含的索引：主键自动、所有外键 B-tree、`(owner_id, created_at DESC)` 复合索引、状态过滤 `(status, created_at)` 或 `(is_deleted, updated_at)`、全文检索 GIN 索引（`to_tsvector`）、向量列 IVFFlat 索引（`lists = max(行数/1000, 100)`）。

单表索引不超过 6 个（含主键和外键），超过则评审合并复合索引。复合索引列顺序：等值条件在前 → 排序条件在中 → 范围条件在后。

**大表预判与应对**

| 表 | 增长速度 | 一期策略 |
|----|----------|----------|
| `chunks` | 每次上传 50-500 行，长期可达百万 | `(document_id)` 单列 + `(kb_id, chunk_index)` 复合索引，预留 HASH 分区 |
| `messages` | 年增量 < 20 万行 | `(conversation_id, created_at)` 复合索引，一期够用 |
| `agent_executions` | 年增量 < 5 万行 | `(agent_id, created_at DESC)` 索引 |
| `workflow_executions` | 年增量 < 2 万行 | `(workflow_id, created_at DESC)` 索引 |

大表处理策略（仅 > 100 万行时启用）：按 `created_at` 月分区 → 超 1 年数据归档到 `_archive` 表 → `chunks` 表按 `knowledge_base_id` HASH 分区。建表时 `COMMENT ON TABLE` 标注预计增速。

**分页查询注意事项**

禁用 `OFFSET + LIMIT` 深分页（offset > 1000）。统一用游标分页：`WHERE created_at < :cursor ORDER BY created_at DESC LIMIT 20`。列表接口返回 `next_cursor`，`page_size` 默认 20 最大 100。导出全量走异步任务。

**通用字段约定**

每张业务表必含：`id UUID PK DEFAULT gen_random_uuid()`、`created_at TIMESTAMPTZ DEFAULT now()`、`updated_at TIMESTAMPTZ DEFAULT now()`。有用户归属加 `owner_id UUID NOT NULL REFERENCES users(id)` + 索引。有软删除加 `is_deleted BOOLEAN DEFAULT FALSE`。执行记录表加 `status VARCHAR(20) NOT NULL` + `error_message TEXT` + `started_at/finished_at TIMESTAMPTZ`。向量表加 `embedding vector(1536)` + `chunk_index INTEGER NOT NULL`。

## 5. 外部 LLM 调用方案 🔴

统一封装在 `provider/base.py`。

### 并发模型

| 机制 | 做法 |
|------|------|
| 并发方式 | async/await，**不引入线程池**（LLM 调用是纯 I/O 等待） |
| 连接池 | `httpx.AsyncClient` 单例 / provider，启动建、关闭释放 |
| 并发上限 | `asyncio.Semaphore(10)` 限制同时发往 LLM 的请求数 |
| 连接池参数 | `max_connections=20, max_keepalive_connections=10` |

### 超时（五层）

连接 10s ｜ 非流式读取 60s ｜ 流式首 token 30s ｜ 流式 idle 15s ｜ 流式总时长 120s（超时中断并返回已生成内容）

### 重试（白名单 + 指数退避，最多 3 次）

- 可重试：`429`、`5xx`、`ConnectionError`、`TimeoutError`
- 不可重试：`400`、`401`、`402`、`403`
- 退避：1s → 2-4s(jitter) → 4-8s(jitter)
- 流式：首 token 前中断 → 静默重试；已推送部分 token 后中断 → 返回已生成内容 + 中断提示

### 容错（三级降级）

| 级别 | 措施 |
|------|------|
| L1 | 重试（同上，最多 3 次） |
| L2 | Provider 切换：主用失败时切到备用（OpenAI ↔ Anthropic） |
| L3 | 返回友好错误："AI 服务暂时不可用，请稍后重试" |

> 不做熔断 / 健康状态机（见范围护栏）。

## 6. 常用命令 ⏳ 待搭建

约定如下命令，搭建脚手架时落地：

```bash
docker compose up -d                                  # 起全栈（caddy/fastapi/pg/redis）
uvicorn app.main:app --reload                         # 后端开发模式
pytest                                                # 跑测试
ruff check . && ruff format .                         # 后端 lint + 格式化
alembic revision --autogenerate -m "msg"              # 生成迁移
alembic upgrade head                                  # 应用迁移
```

## 7. 部署架构 ⚪

> 完整组件职责、性能瓶颈分析、50→5000 人扩展路径见 `docs/deployment.md`。

### 组件（4 容器，Docker Compose 单机，不引入 K8s）

| 组件 | 镜像 | 职责 |
|------|------|------|
| Caddy | `caddy:2-alpine` | 反向代理 + HTTPS 终端 + 前端静态资源 |
| FastAPI | 自建 `microdify:latest` | 应用服务：HTTP API + SSE 流式 |
| PostgreSQL | `pgvector/pgvector:pg16` | 业务数据 + 向量存储，单一实例 |
| Redis | `redis:7-alpine` | 速率限制 + 文档异步队列 + 工作流状态 |

### 关键实现约束 🔴

- **SSE**：流式生成过程中不持有 PG 连接，只在头尾读写；`pool_size=10`。
- **LLM 调用**：统一经 `provider/` LLMGateway，`Semaphore(10)` 控流 + Redis 限流（`INCR+EXPIRE` 按用户/分钟）。
- **文档解析/嵌入**：走 Redis 队列（`LPUSH/BRPOP`）异步处理，不阻塞请求。
- **Caddy 路由**：`/api/*`→FastAPI:8000（SSE 透传不缓冲）｜`/_next/*`→静态产物（不过 FastAPI）｜`/*`→`index.html`。
- **健康检查端点**：FastAPI 暴露 `GET /health` 返回 200。

### 数据持久化

| 数据 | 存储 | 备份 |
|------|------|------|
| 数据库 | Docker volume → `./data/pg/` | pg_dump 每日，保留 7 天 |
| 上传文件 | Docker volume → `./data/uploads/` | 随 PG 备份一起 |
| Redis | AOF → `./data/redis/` | 非关键，丢失可重建 |
| 日志 | `./data/logs/` | Docker json-file + logrotate 10MB×3 |

### 启动顺序与健康检查

```
PG 健康 → Redis 健康 → FastAPI 健康 → Caddy 接受请求
```

PG `pg_isready`(5s) ｜ Redis `redis-cli PING`(5s) ｜ FastAPI `GET /health`(10s) ｜ Caddy 内建

## 8. 范围护栏 — 明确不做 🔴

工作流并行/循环/子工作流 ｜ 工作流发布为工具 ｜ 多 Agent 协作 / Agent 自主发现工具 ｜ 代码沙箱执行 ｜ 知识管道 DSL ｜ 插件系统 ｜ 多租户/命名空间隔离 ｜ 企业安全合规（RBAC/审计/加密，TLS 交给 Caddy）｜ 多版本 Prompt / A/B 测试 ｜ 模型负载均衡 / 熔断 ｜ Prometheus + Grafana

> 触及以上任意一项前，先停下与维护者确认。
