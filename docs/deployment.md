# microDify 部署架构详解

> 面向人类维护者的部署背景与扩展规划。Agent 执行需要的精简版（组件清单、持久化、启动顺序、关键约束）见根目录 `CLAUDE.md` §7。

## 各组件职责

### Caddy（入口网关）

- HTTPS 终端：自签证书或 Let's Encrypt，内网也走加密
- 反向代理：`/api/*` → FastAPI:8000，SSE 长连接透传不缓冲
- 静态资源：`/_next/*` → Next.js 构建产物，直接返回，不经过 FastAPI
- 兜底路由：`/*` → `index.html`，SPA 客户端路由

### FastAPI（应用服务）

- REST API：认证、知识库 CRUD、工作流管理、Agent 配置等
- SSE 流式：对话 / Agent 推理过程的实时推送
- LLM 调用：通过 provider/ 的 LLMGateway 统一发出，Semaphore(10) 控流
- 健康检查：`GET /health` 返回 200，供 Caddy 和 Docker 探测

### PostgreSQL + pgvector

- 业务数据：用户、Agent、对话记录、工作流定义、Prompt 模板
- 向量存储：知识库 chunk 的 embedding，pgvector IVFFlat 索引
- 全文检索：PG 原生 `tsvector`，支撑 BM25 关键词搜索

### Redis

- 速率限制：`INCR + EXPIRE`，按用户/分钟限制 LLM 调用次数
- 文档队列：`LPUSH / BRPOP` 异步处理上传文档的解析和嵌入
- 工作流状态：执行中的工作流中间状态暂存

### 为什么当前不需要 K8s

50 人并发单机足够；四个服务不需要 10+ 个 K8s 资源；一个人维护 K8s 集群不划算。等需要扩容到千人时，模块边界已是天然服务拆分线。

## 性能瓶颈分析

按严重程度排序，含触发条件和一期是否处理。

| 优先级 | 瓶颈 | 原因 | 触发条件 | 一期处理 |
|--------|------|------|----------|----------|
| 🔴 严重 | LLM API Rate Limit | 所有对话/Agent/工作流最终调 LLM，TPM 易超限 | 集中使用 + Agent 多次调用 | ✅ Semaphore(10) 控流 + Redis 限流 + 重试 + Provider 降级 |
| 🟠 高 | PG 连接池耗尽 | SSE 流式持续 5-30s 长期占用连接，默认池 15 个不够 50 人 | 全员同时发对话消息 | ✅ SSE 不在 streaming 中持有连接，只头尾读写；pool_size=10 |
| 🟠 高 | 文档解析占 CPU | PDF 解析 + 嵌入生成耗时 10-30s，和 API 共用进程 | 上传大 PDF 或同时多文档排队 | ⏳ 一期接受，有 Redis 队列异步化。后期拆独立 worker 进程 |
| 🟡 中 | pgvector 大数据量检索退化 | IVFFlat 在 10 万+ chunk 后延迟上升 | 知识库积累超 1000-2000 份文档 | ❌ 一期 IVFFlat 足够。预留 HNSW 升级路径 |
| 🟡 中 | Redis 单点故障 | 限流失效 / 队列丢失 / 工作流中断 | Redis OOM 或宿主机重启 AOF 损坏 | ⏳ 配好 maxmemory + AOF 持久化，不做哨兵 |
| 🟢 低 | SSE 内存占用 | 50 个 SSE 连接 ≈ 100-250MB | 全员同时对话 | ❌ 容器配 1GB 内存足够 |
| 🟢 低 | 单机不可扩展 | 宿主机故障全站宕机 | 硬件故障 | ❌ 内部工具不需高可用，pg_dump 备份兜底 |

## 扩展路径（50 → 200 → 1000 → 5000+）

**核心原则：先纵向扩展（加资源），再横向拆分（分服务）。不在当前阶段提前解决下阶段的问题。**

| 维度 | 阶段一 (50人) | 阶段二 (200人) | 阶段三 (1000人) | 阶段四 (5000+) |
|------|-------------|---------------|----------------|---------------|
| 机器数 | 1 | 1 | 3 | N |
| 容器数 | 4 | 5 | ~12 | ~20+ |
| 编排 | Compose | Compose | Compose/systemd | K8s |
| 代码结构 | 模块化单体 | 同左 | 同左 + 路由拆分 | 独立服务 |
| PG | 单实例 | 单实例 | 主+只读副本 | 主+多副本+PgBouncer |
| Redis | 单实例 | 单实例 | Sentinel | Sentinel 集群 |
| 静态资源 | Caddy | Caddy | 独立 Nginx | CDN |
| 可观测性 | 结构化日志 | 同左 + 用量表 | 同左 | Prometheus+Grafana+链路追踪 |

**阶段二（200人）触发条件与改动：**

- 触发：文档队列积压 >10 任务 或 FastAPI CPU >60% 或 ~200 人规模
- 改：拆 worker 为独立容器、FastAPI workers=4、PG pool_size=20、Redis maxmemory 256mb
- 不改：不拆服务、不引入 K8s、不做 PG 读写分离、代码结构不动

**阶段三（1000人）触发条件与改动：**

- 触发：单机 CPU >70% 或 PG 连接超时 或 需要按团队核算 Token
- 改：双机（API 层 + 数据层分离）、chat/agent 独立容器 ×2、PG 主+只读副本、Redis Sentinel、静态资源独立 Nginx
- 不改：不引入 K8s、不用 gRPC、代码 `app/` 目录结构不动

**阶段四（5000+）触发条件与改动：**

- 触发：需要弹性伸缩 / 滚动更新零停机 / 灰度发布 / 多团队服务治理
- 改：上 K8s、模块正式拆独立服务（同仓库多 Dockerfile）、消息队列升 Redis Stream、PG 加 PgBouncer + 多副本、可观测性升 Prometheus + Grafana + 链路追踪
- 不改：API 协议（仍 REST+SSE）、数据库类型（仍 PostgreSQL）、LLM 调用接口（`provider/` 不变）、前端框架（Next.js 不变）
