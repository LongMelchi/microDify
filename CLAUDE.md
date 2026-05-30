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

## 4. 外部 LLM 调用方案 🔴

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

## 5. 常用命令 ⏳ 待搭建

约定如下命令，搭建脚手架时落地：

```bash
docker compose up -d                                  # 起全栈（caddy/fastapi/pg/redis）
uvicorn app.main:app --reload                         # 后端开发模式
pytest                                                # 跑测试
ruff check . && ruff format .                         # 后端 lint + 格式化
alembic revision --autogenerate -m "msg"              # 生成迁移
alembic upgrade head                                  # 应用迁移
```

## 6. 部署与运维 ⚪

- **compose 服务**：`caddy`（反代+HTTPS+静态）｜`fastapi`（SSE 流式）｜`pg`（PG16+pgvector）｜`redis`（限流+异步队列+工作流状态）
- **限流**：Redis `INCR + EXPIRE`，单用户/分钟
- **文档处理**：Redis 队列异步解析 + 嵌入，避免大文件阻塞请求
- **优雅关闭**：FastAPI `shutdown` 等待 SSE 连接完成
- **健康检查**：所有容器 `healthcheck` 保证启动顺序
- **日志**：结构化 JSON + Docker 日志轮转（10MB×3）
- **容量参考**：~5-10 QPS 应用层、20-50 SSE 长连接；瓶颈在 LLM API Rate Limit。备份 pg_dump 每日，留 7 天。

## 7. 范围护栏 — 明确不做 🔴

工作流并行/循环/子工作流 ｜ 工作流发布为工具 ｜ 多 Agent 协作 / Agent 自主发现工具 ｜ 代码沙箱执行 ｜ 知识管道 DSL ｜ 插件系统 ｜ 多租户/命名空间隔离 ｜ 企业安全合规（RBAC/审计/加密，TLS 交给 Caddy）｜ 多版本 Prompt / A/B 测试 ｜ 模型负载均衡 / 熔断 ｜ Prometheus + Grafana

> 触及以上任意一项前，先停下与维护者确认。
