# Claude Code Skills 完整手册

> 总计 **60 Skills**，按类别分类，含中文简要说明和触发条件。
> 生成日期：2026-05-26

---

## 一、图表与可视化（3）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **drawio** | 生成流程图、架构图、ER图、时序图、类图、网络拓扑图、线框图等 `.drawio` 文件，可导出 PNG/SVG/PDF | 提到 draw.io / 流程图 / 架构图 / 示意图 / 画图 |
| **FlowForge** | 自然语言转专业 draw.io 图表，11种布局算法+5种配色主题，先出ASCII草图确认再生成XML | "画个流程图" / "draw an architecture diagram" / "帮我画个对比图" |
| **claude-canvas** | 浏览器实时画布，手绘风格可视化，支持视觉问答交互面板 | 架构图/线框图/流程图可视化的交互式白板场景 |

---

## 二、前端开发（16）

### 框架与库
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **react-development** | React 官方文档级别：Hooks、组件、状态管理、Context、Effects、性能优化 | React 项目开发/组件编写/Hooks 使用 |
| **react-patterns** | React 现代模式：组件模式、状态管理策略、可扩展应用架构 | React 架构设计/模式选择 |
| **nextjs-development** | Next.js 全栈：App Router、Server Components、数据获取、路由、API Routes、中间件 | Next.js 项目开发 |
| **vuejs-development** | Vue 3 开发：Composition API、响应式系统、组件、指令、现代模式 | Vue.js 项目开发 |
| **angular-development** | Angular 全栈：组件、指令、服务、依赖注入、路由、响应式编程 | Angular 项目开发 |
| **svelte-development** | Svelte 5 开发：响应式 runes、组件、stores、生命周期、过渡动画 | Svelte 项目开发 |

### 样式与布局
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **tailwind-css** | Tailwind CSS 工具优先框架：核心工具类、暗色模式、自定义配置、组件组合 | Tailwind 样式编写/主题定制 |
| **responsive-design** | 移动优先响应式设计：流式布局、媒体查询、Flexbox、Grid、视口单位 | 响应式布局/移动端适配 |
| **ui-design-patterns** | 通用界面模式：导航、表单、数据展示、反馈、无障碍 | UI 组件设计/交互模式选择 |
| **mobile-design** | 移动端 UX 模式：触摸交互、手势设计、移动优先原则、App 导航 | 移动端 UI/UX 设计 |

### 工程基础
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **javascript-fundamentals** | JavaScript 核心：ES6+ 语法、async/await、闭包、原型、现代模式 | JS 基础问题/语法选择 |
| **frontend-architecture** | 前端架构：组件架构、设计模式、状态管理策略、模块系统、构建工具 | 前端架构设计/技术选型 |
| **typescript-advanced-types** | TypeScript 高级类型：泛型、条件类型、映射类型、模板字面量类型、工具类型 | 复杂类型逻辑/类型安全设计 |
| **jest-react-testing** | React 测试：Jest + React Testing Library 配置、Mock策略、异步测试、Hooks测试 | React 组件测试编写 |

---

## 三、后端开发（19）

### Python
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **fastapi-development** | FastAPI 现代 API：异步模式、Pydantic 验证、依赖注入、生产部署 | FastAPI 项目开发 |
| **fastapi-microservices-development** | FastAPI 微服务：REST API 模式、异步操作、部署策略 | FastAPI 微服务架构 |
| **fastapi** | FastAPI 客服系统专项：工单管理、实时聊天、后端运营 | 客服系统后端开发 |

### Node.js
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **expressjs-development** | Express.js 开发：路由、中间件、请求/响应处理、错误处理、REST API | Express 项目开发 |
| **express-microservices-architecture** | Express 微服务：中间件模式、路由策略、错误处理、生产架构 | Express 微服务设计 |
| **nodejs-development** | Node.js 核心：事件循环、异步模式、Stream、文件系统、HTTP服务器、进程管理 | Node.js 后端开发 |

### Go / Rust / Java
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **golang-backend-development** | Go 后端：并发模式、Web服务器、数据库集成、微服务、生产部署 | Go 后端开发 |
| **rust-systems-programming** | Rust 系统编程：所有权、借用、并发、异步、unsafe、性能优化 | Rust 项目开发 |
| **spring-boot-development** | Spring Boot：自动配置、DI、REST API、Spring Data、Security | Java/Spring 企业应用 |
| **axum-web-framework** | Axum Web 框架：路由、提取器、中间件、状态管理、错误处理、生产部署 | Rust Axum 框架开发 |

### API 协议
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **graphql-api-development** | GraphQL API：Schema设计、查询、变更、订阅、解析器、类型系统、认证授权 | GraphQL API 开发 |
| **grpc-microservices** | gRPC 微服务：Protobuf Schema、服务定义、流模式、拦截器、负载均衡 | gRPC 服务开发 |
| **rest-api-design-patterns** | RESTful API 设计：资源建模、版本策略、HATEOAS、分页、过滤、HTTP最佳实践 | REST API 设计 |
| **oauth2-authentication** | OAuth2 认证：授权流程、令牌管理、PKCE、OpenID Connect、安全最佳实践 | 认证系统开发 |
| **hasura-graphql-engine** | Hasura GraphQL 引擎：即时API、权限、认证、事件触发器、Actions | Hasura 项目 |

### 基础设施
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **redis-state-management** | Redis 状态管理：缓存策略、会话管理、发布/订阅、分布式锁、数据结构 | Redis 缓存/状态管理 |
| **api-gateway-patterns** | API 网关模式：Kong、路由、限流、认证、负载均衡、流量管理 | API 网关架构 |
| **microservices-patterns** | 微服务模式：服务网格、流量管理、熔断器、弹性模式、Istio | 微服务架构设计 |

---

## 四、数据库（8）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **postgresql-database-engineering** | PostgreSQL 工程级：索引策略、查询优化、性能调优、分区、复制、高可用、MVCC、VACUUM | PG 性能优化/架构设计 |
| **postgresql** | PostgreSQL 管理：数据库设计、优化、性能调优、备份恢复、高级查询 | PG 日常管理/运维 |
| **sqlalchemy** | SQLAlchemy ORM：会话管理、查询优化、异步操作、PostgreSQL 集成 | Python ORM 开发 |
| **alembic** | Alembic 数据库迁移管理：版本控制、自动生成、回滚 | 数据库迁移/版本管理 |
| **psycopg** | Psycopg PostgreSQL 适配器：数据库操作、查询优化、数据管理 | Python PG 连接操作 |
| **pandas** | Pandas 数据分析：客服运营数据操作、清洗、聚合 | Python 数据分析 |
| **database-management-patterns** | 数据库管理模式：PostgreSQL/MongoDB 的Schema设计、索引、事务、复制、性能调优 | 数据库架构设计 |
| **vector-database-management** | 向量数据库管理：Pinecone/Weaviate/Chroma、语义搜索、RAG系统、相似度应用 | 向量数据库/AI 应用 |

---

## 五、运维与云服务（12）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **aws-cloud-architecture** | AWS 云架构：计算、存储、数据库、网络、安全、Serverless、成本优化 | AWS 架构设计 |
| **aws-cloud-services** | AWS 云服务：S3、Lambda、DynamoDB、EC2、RDS、IAM、CloudFormation | AWS 服务使用 |
| **terraform-infrastructure** | Terraform IaC：Provider、资源、模块、状态管理、多云模式 | Terraform 基础设施 |
| **terraform-infrastructure-as-code** | Terraform 进阶：模块、状态管理、工作空间、高级模式 | Terraform 高级用法 |
| **docker-compose-orchestration** | Docker Compose 编排：多容器应用、网络、卷、生产部署 | Docker 容器编排 |
| **kubernetes-orchestration** | K8s 编排：工作负载、网络、存储、安全、生产运维 | K8s 集群管理 |
| **ci-cd-pipeline-patterns** | CI/CD 流水线：GitHub Actions、工作流、自动化、测试策略、发布管理 | CI/CD 设计 |
| **observability-monitoring** | 可观测性：Prometheus、Grafana、指标采集、告警、PromQL | 监控告警系统 |
| **enterprise-architecture-patterns** | 企业架构：DDD、事件溯源、CQRS、Saga模式、API网关、Service Mesh | 企业级架构设计 |

---

## 六、UI/UX 设计系统（11）

### 跨平台设计
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **design-router** | 设计路由器：自动判断目标平台（UX/Web/Windows/Android），分派到对应设计Skill | 界面/流程/组件设计需求不明确时 |
| **ux-design** | UX 设计：用户流程、信息架构、表单、引导、仪表盘、空/加载/错误状态设计 | UX/用户流程/线框图/转化优化 |
| **cross-platform-design** | 跨平台UI：一套代码多平台，每个平台用原生风格而非像素克隆。支持 CMP/Tauri/RN/Flutter/MAUI | 跨平台应用设计 |
| **design-tokens** | Design Token 生成与转换：W3C DTCG ↔ Tailwind v4/Compose Material3/SwiftUI/WinUI | Design Token 管理/平台迁移 |

### 平台专属设计
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **web-design** | Web 界面设计：React/Next/Vite/Tailwind，6种美学方向，动效/滚动/排版 | Web 应用/落地页/仪表盘 |
| **android-design** | Android 设计：Material 3/Material You/Pixel风格，5条轨道（Compose/品牌Compose/RN/Flutter/CMP） | Android App 设计 |
| **windows-design** | Windows 设计：WinUI 3/品牌WinUI/Tauri 2/Electron，4条轨道 | Windows 桌面应用设计 |
| **ui-ux-pro-max** | 设计智能工具包：50+风格/161调色板/57字体搭配/99UX准则/25图表类型，10个技术栈 | UI/UX 设计与审查 |

### 设计规范参考
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **material-3** | Material Design 3 (Material You)：30+组件/Design Token/主题/自适应布局/M3 Expressive | MD3/Jetpack Compose MaterialTheme |
| **frontend-design** (插件) | Anthropic 官方：反AI模板风，强制选择美学方向，品牌化设计 | 创建网页/组件/应用界面 |
| **design-system-creation** | 创建设计系统：排版、颜色、组件、文档 | 建立设计标准/组件库 |

---

## 七、接口文档与代码规范（3）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **api-documentation-generator** | API 文档生成器：从代码生成端点文档、OpenAPI 3.0/Swagger规范、Postman Collection、cURL/JS/Python示例 | 需要文档化API/生成Swagger规范 |
| **rest-api-design-patterns** | RESTful API 设计：资源建模、版本策略、HATEOAS、分页、过滤、HTTP最佳实践（同后端部分） | REST API 设计 |
| **graphql-api-development** | GraphQL API 开发：Schema设计、查询/变更/订阅、类型系统、错误处理（同后端部分） | GraphQL API 开发 |

> **关于代码规范**：推荐使用 `CLAUDE.md`（项目根目录）写入团队规范 + PostToolUse Hooks 自动运行 ESLint/Prettier/Ruff 等格式化工具，而非依赖单独的 Skill。

---

## 八、工作流与流程管理（7）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **brainstorming** | 创意前必用：强制探索3+种方案及权衡，再写代码 | 任何新功能/组件/功能开发前 |
| **writing-plans** | 编写实施计划：将复杂任务分解为5-10个可验证步骤 | 多步骤任务/需求明确后 |
| **executing-plans** | 执行计划：按步骤执行并每步验证 | 已有书面计划时 |
| **subagent-driven-development** | 子代理驱动开发：并行执行独立任务 | 多个独立子任务并行处理 |
| **dispatching-parallel-agents** | 并行代理调度：2+个无依赖任务同时进行 | 多个独立任务并行 |
| **test-driven-development** | TDD 测试驱动：先写测试再写实现，提前捕获边界情况 | 任何功能/修复开发前 |
| **verification-before-completion** | 完成前验证：必须运行验证命令确认通过才能声称完成 | 声称完成/修复/通过前 |

---

## 九、调试与代码质量（6）

| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **systematic-debugging** | 系统化调试：观察→假设→测试→修复四阶段 | 遇到Bug/测试失败/异常行为 |
| **requesting-code-review** | 请求代码审查：5个并行代理（安全/性能/正确性/风格/测试） | 完成任务/主要功能/合并前 |
| **receiving-code-review** | 接收代码审查反馈：技术严谨性验证，非表演性同意 | 收到 Code Review 意见时 |
| **code-review** (插件) | Code Review PR：审查当前 diff 的正确性 | PR 代码审查 |
| **security-review** | 安全审查：审查当前分支待处理更改的安全性 | 安全审计 |
| **writing-skills** | 编写/编辑 Skill：创建或修改自定义 Skill | 创建新 Skill/编辑现有 Skill |

---

## 十、辅助工具与命令（9）

### Stark 设计命令
| 命令 | 说明 | 触发条件 |
|------|------|---------|
| **/stark** | Stark 设计入口：按平台生成/改进 UI/UX，自动路由到对应设计Skill | `/stark [platform] <描述>` |
| **/stark-audit** | Stark 审计：对 UI/UX 代码/截图进行启发式评估和平台规范检查 | `/stark-audit [文件/截图路径]` |
| **/stark-reference** | Stark 参考分析：分析真实产品UI/UX参考，提取结构化参考信息 | `/stark-reference <产品/截图/URL>` |
| **/stark-translate** | Stark 跨平台翻译：将一个平台的UI翻译到另一个平台 | `/stark-translate [源平台] [目标平台]` |
| **/stark-assets** | Stark 资源规划：规划UI资源，包括参考、图标、字体、产品模型 | `/stark-assets <项目描述>` |

### 系统工具
| Skill | 说明 | 触发条件 |
|-------|------|---------|
| **find-skills** | 发现和安装 Skills：搜索社区 Skill 并安装 | "如何做X" / "找个Skill" |
| **using-superpowers** | Superpowers 使用指南：如何使用 Skill 体系 | 每次对话开始时 |
| **using-git-worktrees** | Git Worktree 隔离：为功能开发创建隔离工作区 | 需要隔离开发环境 |
| **update-config** | 配置管理：修改 settings.json 中的权限/环境变量/Hooks | 修改设置/配置 |
| **finishing-a-development-branch** | 完成开发分支：合并/PR/清理的结构化选项 | 实现完成、测试通过后 |
| **claude-api** | Claude API / Anthropic SDK 开发：提示缓存、模型迁移、Managed Agents | 使用 Anthropic SDK 开发 |
| **init** | 初始化 CLAUDE.md：为代码库生成文档 | 初始化项目文档 |

---

## 快速查找索引

### 按技术栈查找
- **React/Next.js**: react-development, react-patterns, nextjs-development, jest-react-testing, tailwind-css, web-design
- **Vue**: vuejs-development, web-design
- **Angular**: angular-development
- **Svelte**: svelte-development
- **Python/FastAPI**: fastapi, fastapi-development, fastapi-microservices-development, sqlalchemy, alembic, psycopg, pandas
- **Node.js/Express**: expressjs-development, express-microservices-architecture, nodejs-development
- **Go**: golang-backend-development
- **Rust**: rust-systems-programming, axum-web-framework
- **Java**: spring-boot-development
- **Kotlin/Android**: android-design, material-3

### 按任务类型查找
- **画图**: drawio, FlowForge, claude-canvas
- **设计UI**: web-design, android-design, windows-design, ui-ux-pro-max, frontend-design
- **写API**: fastapi-development, expressjs-development, rest-api-design-patterns, graphql-api-development, grpc-microservices
- **写文档**: api-documentation-generator
- **调试**: systematic-debugging
- **审查代码**: requesting-code-review, receiving-code-review, code-review, security-review
- **部署运维**: docker-compose-orchestration, kubernetes-orchestration, terraform-infrastructure, ci-cd-pipeline-patterns
- **数据库设计**: postgresql-database-engineering, database-management-patterns, vector-database-management

---

# 大型软件工程项目推荐工作流

> 基于本手册中的 60 个 Skill，按 6 个阶段组织完整的项目开发流程。

## 总览

```
Phase 0 (架构) → Phase 1 (基础设施) → Phase 2 (数据库) → Phase 3+4 并行 (前后端) → Phase 5 (审查) → Phase 6 (部署)
```

---

## Phase 0：项目启动与架构设计

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 0.1 | **brainstorming** | 探索技术选型：后端语言/框架、前端框架、数据库、部署方案。至少对比 3 种方案并列出权衡 |
| 0.2 | **drawio** / **FlowForge** | 绘制系统架构图、ER 图、核心业务流程图。先出 ASCII 草图确认，再生成正式图 |
| 0.3 | **writing-plans** | 将整体项目拆解为阶段性子计划，每步有明确的验收标准 |
| 0.4 | **design-router** | 根据目标用户确定 UI 平台和设计方向 |

**产物**：架构图 + 技术选型文档 + 总体计划

---

## Phase 1：基础设施搭建

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 1.1 | **init** | 生成项目 `CLAUDE.md`，写入架构约束、命名规范、非标准约定 |
| 1.2 | **update-config** | 配置 PostToolUse Hooks：保存后自动运行 ESLint/Prettier/Ruff/Black |
| 1.3 | **using-git-worktrees** | 为新功能创建隔离工作区，避免相互污染 |
| 1.4 | **docker-compose-orchestration** | 搭建本地开发环境：应用容器 + 数据库 + Redis + 依赖服务 |
| 1.5 | **ci-cd-pipeline-patterns** | 设计 CI/CD 流水线：lint → test → build → deploy |
| 1.6 | **terraform-infrastructure** | 如果是云项目：定义基础设施即代码 |

**产物**：开发环境 + CI/CD 流水线 + IaC 配置

---

## Phase 2：数据库设计

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 2.1 | **database-management-patterns** | 设计 Schema：表结构、索引策略、事务边界、复制方案 |
| 2.2 | **postgresql-database-engineering** | 评审设计：索引正确性、查询计划预估、分区考虑、连接池配置 |
| 2.3 | **alembic** | 初始化迁移系统，编写首次迁移脚本，确认回滚策略 |

**产物**：数据库 Schema + 迁移脚本

---

## Phase 3：后端开发

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 3.1 | **rest-api-design-patterns** / **graphql-api-development** | 设计 API：资源建模、端点定义、版本策略、错误格式规范 |
| 3.2 | **oauth2-authentication** | 设计认证授权：JWT/OAuth2 流程、角色权限模型 |
| 3.3 | **test-driven-development** | TDD 模式开发：先写测试→确认失败→写实现→重构 |
| 3.4 | **fastapi-development** / **expressjs-development** / **golang-backend-development** / **spring-boot-development** | 按选型用对应框架 Skill 开发业务逻辑 |
| 3.5 | **redis-state-management** | 集成缓存：热点数据缓存、会话管理、分布式锁 |
| 3.6 | **sqlalchemy** / **psycopg** | ORM 查询优化、N+1 问题排查、事务管理 |
| 3.7 | **api-documentation-generator** | 从代码自动生成 OpenAPI 3.0 规范 + Postman Collection |

**产物**：可运行的 API + 测试 + API 文档

---

## Phase 4：前端开发（可与 Phase 3 并行）

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 4.1 | **ux-design** | 设计用户流程：信息架构、导航结构、表单、空/加载/错误状态 |
| 4.2 | **web-design** / **frontend-design** | 选择美学方向，品牌化设计，反 AI 模板风 |
| 4.3 | **design-system-creation** / **design-tokens** | 建立 Design Token 系统：颜色、字体、间距、组件变量 |
| 4.4 | **tailwind-css** / **responsive-design** | 实现响应式布局和样式系统 |
| 4.5 | **react-development** / **nextjs-development** / **vuejs-development** / **angular-development** | 按选型用对应框架 Skill 开发 |
| 4.6 | **typescript-advanced-types** | 复杂类型逻辑、泛型工具类型、API 类型安全封装 |
| 4.7 | **jest-react-testing** | 组件测试、Hooks 测试、集成测试 |
| 4.8 | **/stark** + **/stark-audit** | UI 实现后审计：平台规范检查、UX 启发式评估、具体行号报告 |

**产物**：可用的前端应用 + 测试 + 设计审计报告

---

## Phase 5：集成、审查与质量

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 5.1 | **requesting-code-review** | 请求全面审查：5 个并行代理（安全性/性能/正确性/代码风格/测试覆盖） |
| 5.2 | **security-review** | 专项安全审查：认证流程、授权逻辑、数据泄露风险 |
| 5.3 | **systematic-debugging** | 发现 Bug 时：观察现象→形成假设→设计测试→修复验证 |
| 5.4 | **verification-before-completion** | **最终关卡**：跑全部测试、检查无硬编码值、确认文档更新 |

**产物**：Review 报告 + 安全审计 + Bug 修复记录

---

## Phase 6：部署与运维

| 步骤 | 使用的 Skill | 做什么 |
|------|-------------|--------|
| 6.1 | **docker-compose-orchestration** / **kubernetes-orchestration** | 生产环境容器编排、健康检查、资源限制 |
| 6.2 | **observability-monitoring** | Prometheus + Grafana 监控、告警规则、关键指标面板 |
| 6.3 | **finishing-a-development-branch** | 合并策略选择、PR 创建、清理工作区 |
| 6.4 | **enterprise-architecture-patterns** | 长期演进：DDD 重构方向、CQRS 拆分时机、Service Mesh 引入评估 |

**产物**：生产部署 + 监控面板 + 合并 PR

---

## 并行执行策略

大型项目中，以下阶段可以并行推进：

| 并行组 | 涉及 Skill | 说明 |
|--------|-----------|------|
| Phase 3 ↔ Phase 4 | 后端 + 前端 | 用 **dispatching-parallel-agents** 同时启动前后端开发 |
| 多模块并行 | **subagent-driven-development** | 同一阶段内多个独立模块并行开发 |

---

## 关键原则

1. **brainstorming 必须最先用** — 跳过此步骤导致方向错误，返工成本最高
2. **test-driven-development 贯穿 Phase 3/4** — 每个功能先写测试再实现
3. **verification-before-completion 必须最后用** — 严禁在验证通过前声称完成
4. **api-documentation-generator 跟随开发持续更新** — 不等最后补文档
5. **code-review + security-review 在合并前必执行** — 生产上线前的两道防线
6. **drawio / FlowForge 在每个阶段开始前画图** — 架构图、ER 图、流程图，先想清楚再动手

---

# 附录：AI 代码智能 Skills（CodeGraph + Understand Anything + Karpathy）

> 以下三个 Skill 组合为 AI Agent 提供代码库深度理解能力。生成日期：2026-05-27

---

## A. 三个工具的定位对比

| 维度 | Karpathy Guidelines | CodeGraph | Understand Anything |
|------|------|------|------|
| **做什么** | 约束 AI 编码行为 | 精准依赖分析 | 语义理解 + 可视化 |
| **触发方式** | 手动激活 `Skill()` | 自动（MCP 被动增强） | 斜杠命令 `/` |
| **输出** | 行为约束规则 | SQLite 图数据库 | `knowledge-graph.json` |
| **最佳场景** | 控制 AI 不乱改 | 找"改这个会炸哪" | 理解"这段代码在干什么" |

---

## B. Karpathy Guidelines

**技能名**: `karpathy-guidelines`

**用途**: 约束 AI 编码行为，减少常见 LLM 错误——避免过度工程化、擅自重构、未澄清就动手。

**触发条件**: 写代码、审查代码、重构代码时手动激活。

**使用说明**: 在编码类任务前运行 `Skill(karpathy-guidelines)` 激活其约束。

**四条规则**:
1. **Think Before Coding** — 有疑问先问，不自己猜
2. **Simplicity First** — 能 50 行绝不 200 行
3. **Surgical Changes** — 只改该改的，不顺手重构
4. **Goal-Driven Execution** — 定义可验证的成功标准

**案例**:
```
用户: 给 user 模块加个手机号字段
AI（无约束）: 顺便把 user 模块全部重构了一遍，改了 12 个文件
AI（有 karpathy-guidelines）: 只改了 user model + schema + migration，3 个文件
```

---

## C. CodeGraph（32 个子技能）

**核心技能**: `codragraph-cli`

**用途**: 将代码库预索引为知识图谱（函数/类/调用关系/依赖），此后 AI 通过 MCP 查图理解代码，而非逐个 grep 读文件。

**初始化**:
```bash
npx @codragraph/cli analyze          # 在项目根目录运行，建立索引
npx @codragraph/cli setup            # 配置 MCP 到编辑器（一次性）
```

**触发条件**: 索引后，以下场景 AI 自动调用对应的 codragraph 工具。

### C.1 代码探索类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-exploring` | 理解架构、追踪执行流 | "这个函数被谁调用了？" |
| `codragraph-onboarding` | 生成新人入职指南 | "我刚接手这个项目，帮我梳理结构" |
| `codragraph-api-surface` | 枚举公开 API | "这个包导出了哪些接口？" |
| `codragraph-project-switcher` | 多项目切换 | "我有 3 个仓库，切换到 XXX 项目" |
| `codragraph-guide` | CodeGraph 自身使用帮助 | "CodeGraph 有哪些可用工具？" |

### C.2 安全变更类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-impact-analysis` | 修改前分析影响范围 | "改这个函数会不会炸？" |
| `codragraph-cross-repo-impact` | 跨仓库影响分析 | "这个 proto 改了，哪些服务受影响？" |
| `codragraph-refactoring` | 安全重构 | "把这个类拆成两个模块" |

### C.3 质量审计类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-dead-code` | 死代码检测 | "哪些函数/类已经没人用了？" |
| `codragraph-test-coverage` | 测试覆盖缺口 | "哪些执行流没有测试覆盖？" |
| `codragraph-security-audit` | 安全审计 | "有没有绕过认证的路径？" |
| `codragraph-observability-coverage` | 可观测覆盖 | "哪些函数没有打日志？" |
| `codragraph-supply-chain-audit` | 依赖风险审计 | "哪些第三方包用得最深？" |
| `codragraph-config-audit` | 配置审计 | "哪些环境变量定义了但没用到？" |
| `codragraph-perf-hotspots` | 性能热点预筛 | "哪些函数被所有入口调用？" |

### C.4 调试追踪类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-debugging` | Bug 追溯 | "这个错误是从哪一层传上来的？" |
| `codragraph-data-lineage` | 数据血缘追踪 | "这个表被哪些函数读写？" |
| `codragraph-sql-tracing` | SQL 调用链追踪 | "这个 SELECT 在代码哪里构造的？" |

### C.5 PR/变更管理类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-pr-review` | PR 审查 | "这个 PR 改了什么？有没有风险？" |
| `codragraph-migration-tracking` | 迁移进度跟踪 | "从 X 迁移到 Y 完成了多少？" |
| `codragraph-notebook-context` | Notebook 项目导航 | "这些 Jupyter Notebook 做了什么？" |

### C.6 Git 工作流类

| 技能 | 用途 | 案例 |
|------|------|------|
| `codragraph-git-rebase-vs-merge` | rebase vs merge 决策 | "这个分支该 rebase 还是 merge？" |
| `codragraph-git-bisect` | 二分法定位回归 Bug | "是哪次提交引入的问题？" |
| `codragraph-git-recovery` | 恢复丢失的工作 | "我 reset --hard 搞丢了提交" |
| `codragraph-git-force-push` | 安全强制推送 | "force push 安全吗？" |
| `codragraph-git-history-rewrite` | 提交历史重写 | "把 WIP 提交 squash 掉" |
| `codragraph-git-worktree` | 并行分支工作 | "同时处理 hotfix 和 feature" |
| `codragraph-gh-pr-workflow` | GitHub PR 工作流 | "创建草稿 PR、请求审查" |
| `codragraph-gh-issue-workflow` | GitHub Issue 管理 | "分类、打标签、关联 PR" |
| `codragraph-gh-actions-debug` | GitHub Actions 排错 | "CI 为什么失败了？" |
| `codragraph-gh-release-workflow` | 发布流程 | "打版本号、生成 Release Notes" |

### C.7 CodeGraph 使用案例（真实对话举例）

**新人入职场景**
```
用户: 我刚接手这个项目，帮我梳理结构
AI 调用 codragraph-onboarding
→ 自动识别入口文件、架构分层、功能模块
→ 按依赖拓扑顺序生成学习路径：
   ① 先看 shared/ 基础层（database.py, security.py）
   ② 再看 agents/ 模块（核心执行器）
   ③ 最后看 workflows/（编排层）
→ 附带每个模块的摘要和关键函数列表
```

**修改前影响分析**
```
用户: 我要改 agents/react_executor.py 里的 execute() 函数，会炸吗？
AI 调用 codragraph-impact-analysis
→ 从知识图谱查询 execute() 的调用链
→ 输出：
   直接调用方: agents/routes.py:82, chat/sse_handler.py:45
   间接影响: workflows/engine.py (通过 chain_of_thought)
   风险评估: 中等——改了执行器逻辑会连锁影响 chat SSE 推送
   建议: 先跑 chat/tests/ 和 agents/tests/ 确保不破
```

**死代码清理**
```
用户: 有没有没人用的函数，帮我找出来
AI 调用 codragraph-dead-code
→ 遍历图谱，检查每个符号的 caller 数量
→ 输出：
   tools/builtin/search.py:web_search_v1() — 0 调用方（已被 v2 替换）
   knowledge/parser.py:parse_pdf() — 0 调用方（只保留了 parse_docx）
   建议: 这 2 个可以安全删除，无测试覆盖也无调用方
```

**安全审计**
```
用户: 有没有绕过认证的 API 路径？
AI 调用 codragraph-security-audit
→ 查询所有路由节点的 auth 中间件依赖
→ 输出：
   ⚠  /api/v1/chat/export    — 无 auth 守卫
   ⚠  /api/v1/tools/callback  — 仅检查了 token，未验证权限范围
   ✓  其余 23 个路由均正常
```

**SQL 调用链追踪**
```
用户: 这个 INSERT INTO agent_executions 在哪些地方执行的？
AI 调用 codragraph-sql-tracing
→ 从 SQL 字符串反查构造点
→ 输出：
   agents/service.py:147 — AgentService.execute()
   workflows/engine.py:89 — WorkflowEngine.step_callback()
   chat/sse_handler.py:112 — SSEHandler.on_complete()
   共 3 个调用点，都在正常业务路径内
```

**Bug 追溯**
```
用户: Chat 回复到一半就断了，报 "connection reset"，帮我追一下
AI 调用 codragraph-debugging
→ 从错误信息定位到 sse_handler.py
→ 沿调用链上溯：
   sse_handler.py:112 → agents/react_executor.py:237 → shared/llm_client.py:89
→ 发现 llm_client.py 的 timeout 设了 30s，但模型响应偶尔超时
→ 建议：给 llm_client 加重试逻辑或用 Semaphore 排队控制
```

**批量重构**
```
用户: 把整个项目里的 user_id 参数名改成 account_id
AI 调用 codragraph-refactoring
→ 从图谱查询所有出现 user_id 的位置
→ 输出：
   影响范围: 47 处（12 个文件）
   安全路径: 按依赖顺序从上往下改
   agents/: 8 处 → workflows/: 6 处 → chat/: 4 处 ...
   附带自动生成的多文件重命名脚本
```

**测试覆盖缺口**
```
用户: 哪些执行流还没写测试？
AI 调用 codragraph-test-coverage
→ 对比入口点 → 导出函数的调用链 vs tests/ 下的测试引用
→ 输出：
   未覆盖流程:
   tools/importer.py:import_from_url() — 无测试
   knowledge/chunker.py:semantic_split() — 无测试
   agents/react_executor.py:handle_tool_error() — 无测试
   覆盖率: 61%，建议优先补上 3 个核心路径
```

---

## D. Understand Anything（9 个子技能）

**用途**: 将代码库变成可对话的知识图谱，Tree-sitter 保证调用链准确，LLM 提供语义理解。

**触发条件**: 通过斜杠命令 `/` 触发。

### D.1 技能列表

| 技能/命令 | 用途 | 案例 |
|------|------|------|
| `/understand` | 全量扫描代码库，构建知识图谱 | "帮我分析这个项目" |
| `understand-chat` | 自然语言向知识图谱提问 | "支付流程是怎么走的？" |
| `understand-dashboard` | 打开可视化仪表盘 | "给我看架构图" |
| `understand-diff` | 分析 Git diff 影响范围 | "这个 PR 改了哪些关键路径？" |
| `understand-domain` | 提取业务领域，生成领域流图 | "这个模块属于哪个业务域？" |
| `understand-explain` | 深度解析单个文件/函数 | "这个 Controller 做了什么？" |
| `understand-knowledge` | 分析 Wiki/知识库并生成图谱 | "从文档中提取关键实体" |
| `understand-onboard` | 生成新人入职指南 | "新同事应该从哪开始看代码？" |

### D.2 使用说明

**第一步**：在项目根目录运行 `/understand`，启动 7 Agent 流水线扫描代码库。

**第二步**：扫描完成后，使用以下命令：
- `/understand-dashboard` 打开可视化页面
- `understand-chat` 用自然语言提问
- `understand-explain` 分析特定文件

### D.3 Understand Anything 使用案例（真实对话举例）

**全量扫描 + 提问**
```
用户: /understand
AI 启动 7 Agent 流水线扫描，9.9s 后完成
   178 节点 | 322 边 | 索引完毕

用户: understand-chat 这个项目的核心流程是什么？
AI: 从知识图谱分析——
   1. 用户通过 /api/v1/chat 发起对话
   2. ChatService 创建会话 → 交给 AgentExecutor
   3. AgentExecutor 用 ReAct 循环：推理 → 调工具 → 观察 → 继续
   4. 结果通过 SSE 逐字推回前端
   关键模块: agents/ → tools/ → chat/sse_handler.py
```

**可视化仪表盘**
```
用户: /understand-dashboard
AI 启动本地服务 → 浏览器打开交互式图谱
   左侧: 架构分层树（API → Service → Data）
   中间: DAG 节点图，点击节点展开上下游
   右侧: 节点详情（摘要、调用方、被调用方、所属业务域）
```

**PR 审查**
```
用户: /understand-diff
AI 分析当前分支和 main 的 diff
→ 输出：
   改动文件: 7 个
   agents/react_executor.py: 新增 handle_tool_error()
   agents/service.py: execute() 流程调整
   chat/sse_handler.py: 错误时推送 error 事件
   影响范围:
   - 直接: agents 模块、chat 模块
   - 间接: workflow 调用 agent 执行的回调
   风险: 低（仅新增错误处理路径，未改主流程）
   建议: 在 agents/tests/ 中加一个工具调用异常用例
```

**业务领域提取**
```
用户: /understand-domain
AI 从代码中提取业务领域并生成流图:
→ 用户管理 → 注册 → 登录（简单账户，无 RBAC）
→ Agent 管理 → 创建 Agent → 配置工具 → 发布为 API
→ 对话 → 发起会话 → ReAct 推理 → SSE 流式返回
→ 知识库 → 上传文档 → 解析 → 分块 → 嵌入 → 向量检索
→ 工作流 → 编排节点 → 条件分支 → 执行 → 返回结果
```

**深度解析单个文件**
```
用户: understand-explain agents/react_executor.py
AI: react_executor.py — Agent 的 ReAct 推理循环
   - ReActExecutor 类：核心推理执行器
   - execute() 方法：主循环入口
     1. 构建 system prompt + 工具列表
     2. while 未完成：调 LLM → 解析 Thought/Action → 执行工具 → 喂回结果
     3. 循环控制: max_steps=15, 防死循环
   - handle_tool_error()：工具调用失败时的降级处理
   调用链: ChatService → AgentService.execute() → ReActExecutor.execute()
   被依赖: 被 workflows/engine.py 调用（工作流中的 LLM 节点）
```

**生成新人入职指南**
```
用户: understand-onboard
AI 生成《microDify 新人上手指南》:
   1. 项目定位: 轻量级 AI Agent 平台，基于 Dify 思想构建
   2. 技术栈: FastAPI + Vue 3 + PostgreSQL + ChromaDB + Redis
   3. 阅读顺序:
      第一步: app/shared/（基础设施层）
      第二步: app/agents/（核心：Agent 执行器 + ReAct）
      第三步: app/chat/（SSE 流式对话）
      第四步: app/workflows/（工作流引擎）
      第五步: app/knowledge/（知识库：解析 → 分块 → 检索）
      第六步: app/tools/（内置工具 + OpenAPI 导入）
   4. 本地启动: docker compose up → http://localhost:8000/docs
   5. 关键文件: CLAUDE.md（项目约定）、.env.example（环境变量）
```
