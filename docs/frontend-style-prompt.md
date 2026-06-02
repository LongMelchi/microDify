# microDify 前端风格 Prompt

> 供 AI Agent 执行的前端设计规范，与 CLAUDE.md §1-3 的代码组织规范互补。
> **图例：🔴 必须遵守 | ⚪ 参考背景**

---

## 产品定位

microDify 是一个 AI Agent 开发平台，面向技术团队内部使用（20-50 人），主要用户是开发者和技术管理者。界面以管理后台为主——大量表格、表单、配置页面，加上一个 SSE 流式对话交互页面。

## 视觉风格：Clay 风 + 科技感

**风格：浅底 + 深色侧边栏 + Clay 硬阴影。** 整体用浅色背景保持信息可读性（管理后台表格多，深色底长时间看眼睛累），但不要太素——侧边栏用深色底，卡片和关键交互元素用粗边框 + 硬阴影制造设计感和品牌辨识度。

参考：Notion（Clay 卡片的硬阴影）、Linear（信息密度的克制感）、Supabase（深色侧边栏 + 浅内容区）。

## 设计令牌（CSS 变量体系）🔴

### 品牌色

```
--color-primary:        #5B5FE3;  /* 蓝紫主色，科技感 */
--color-primary-hover:  #4A4ECC;
--color-primary-light:  #EEEDFC;  /* 主色浅底 */
--color-secondary:      #3ECF8E;  /* 薄荷绿，数据/状态指示 */
--color-secondary-hover:#2FB878;
--color-secondary-light:#E6F9F1;  /* 辅色浅底 */
--color-accent:         #F59E0B;  /* 暖橙，CTA 强调 / 警告 */
--color-accent-hover:   #D97706;
--color-accent-light:   #FFF7ED;  /* 点缀浅底 */
```

### 中性色

```
--color-bg:             #F8F9FC;  /* 页面底色，浅灰蓝 */
--color-surface:        #FFFFFF;  /* 卡片/容器白 */
--color-sidebar:        #1E1E2E;  /* 深色侧边栏 */
--color-sidebar-hover:  #2D2D44;
--color-text:           #1A1A2E;  /* 正文，接近黑 */
--color-text-secondary: #6B7280;  /* 辅助文字 */
--color-text-tertiary:  #9CA3AF;  /* 占位/禁用文字 */
--color-border:         #DDE1E8;  /* 默认边框 */
--color-divider:        #E5E7EB;  /* 分割线 */
```

### 语义色

```
--color-success:        #10B981;  /* 成功 */
--color-warning:        #F59E0B;  /* 警告 */
--color-error:          #EF4444;  /* 错误 */
--color-info:           #3B82F6;  /* 信息 */
```

### 圆角（形状一致性锁定 🔴）

```
--radius-sm:   8px;    /* 小元素: tag / badge / input */
--radius-md:   12px;   /* 默认: button / card / dropdown */
--radius-lg:   16px;   /* 大卡片 / modal */
--radius-full: 9999px; /* 药丸: 状态指示器 / 标签 */
```

### 阴影（Clay 风硬阴影，着色非纯黑 🔴）

```
--shadow-sm:   2px 2px 0 rgba(26, 26, 46, 0.10);  /* 小按钮 / tag */
--shadow-md:   4px 4px 0 rgba(26, 26, 46, 0.10);  /* 默认卡片 / 按钮 */
--shadow-lg:   6px 6px 0 rgba(26, 26, 46, 0.08);  /* modal / 大卡片 */
--shadow-hover: translate(2px, 2px) + shadow 减弱; /* hover 时阴影收缩 */
```

### 间距（4pt 体系）

```
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
```

### 字体 🔴

```
--font-sans:  "Inter", system-ui, sans-serif;        /* UI 正文 */
--font-mono:  "JetBrains Mono", "Fira Code", monospace; /* 代码/数据 */
```

| 场景 | 字号/行高/字重 |
|------|---------------|
| 页面标题 | 24px / 1.3 / 700 |
| 区块标题 | 18px / 1.4 / 600 |
| 正文 | 14px / 1.6 / 400 |
| 辅助文字 | 12px / 1.5 / 400 |
| 代码/数据 | 13px / 1.7 / 500 (JetBrains Mono) |
| 按钮 | 14px / 1 / 600 |

### 动效 🔴

```
--transition-fast:   150ms cubic-bezier(0.16, 1, 0.3, 1);  /* hover / focus */
--transition-normal: 250ms cubic-bezier(0.16, 1, 0.3, 1);  /* 展开 / 收起 */
--transition-slow:   350ms cubic-bezier(0.16, 1, 0.3, 1);  /* modal 进出 */
```

动效原则：只动 `transform` + `opacity`，禁动 `width/height`。尊重 `prefers-reduced-motion`。

## 组件规范 🔴

### 按钮

| 变体 | 用途 |
|------|------|
| `btn-primary` | 主 CTA，蓝紫底 + 白字 + 3px 边框 + 硬阴影 |
| `btn-secondary` | 次要操作，白底 + 文本色 + 3px 边框 + 硬阴影 |
| `btn-danger` | 危险操作，红色文字 + 红色边框 |
| `btn-ghost` | 最低优先级，无边框无背景，hover 露出 |

- hover：阴影收缩 + 平移 `translate(2px, 2px)`
- active：`scale(0.98)` + 阴影消失
- disabled：opacity 0.4 + cursor not-allowed
- 最小触摸目标：44×44px 🔴
- 加载态：按钮等宽，spinner 替换文字，禁止点击

### 卡片

- 白底 + 3px 边框(`var(--color-text)`) + `--shadow-md`
- hover：卡平移 + 阴影收缩
- 卡片内信息层次：标题 → 描述 → 元数据（用文字色区分，不用额外边框）
- 统计卡片：大号数字用 `font-mono`，趋势箭头用辅色/红色

### 表单

- 标签在输入框上方（不占位符当标签）🔴
- 输入框：白底 + 2px 边框(`--color-border`) + `--radius-sm`，focus 时边框变主色
- 错误态：边框变红 + 错误文本在字段下方
- 禁用态：灰色背景 + 降低不透明度
- 必填字段用红色星号
- 高度 ≥ 44px

### 表格

- 表头：浅灰底 + 粗体 + `border-bottom: 2px solid var(--color-border)`
- 行：斑马纹（交替浅灰），hover 高亮
- 最后一行无下划线
- 操作列统一右对齐
- 空态：居中显示引导文案 + 行动按钮
- 加载态：骨架屏（3-5 行灰色脉冲条）

### 标签 & 徽章

- Tag：`--radius-full` 药丸，内边距 2px 10px
- 6 种语义色变体：default / primary / success / warning / error / info
- 小号 12px / 中号 14px
- 计数徽章：右上角红色药丸数字

### 侧边栏

- 深色底(`--color-sidebar`) + 白色文字
- 宽度：220px 固定
- 菜单项：32px 高 + hover 变浅 + active 左侧 3px 主色指示条
- 底部用户区：分割线 + 头像 + 用户名

### 对话气泡（Chat 模块专属）

- 用户气泡：右对齐，主色浅底 + 文本色字
- AI 气泡：左对齐，白底 + 3px 边框 + 硬阴影
- 流式生成中：光标闪烁动画 `|` + "正在思考..." 小字
- 知识库引用：AI 气泡下方小卡片，显示引用文档标题

### 模态框

- 居中弹出 + backdrop 模糊（`backdrop-filter: blur(4px)`）
- 3px 边框 + `--shadow-lg`
- 标题 + 内容 + 底部按钮行
- Escape 关闭 + 点击 backdrop 关闭

### Toast / 通知

- 右上角弹出，4 种变体：success / error / warning / info
- 3-5 秒自动消失
- 带图标 + 文字 + 关闭按钮
- 使用 `aria-live="polite"`

### 加载状态

- 骨架屏优先（匹配内容形状），避免全局 spinner
- 表格加载：3-5 行灰色脉冲条
- 卡片加载：灰色矩形 + shimmer 动画
- 按钮加载：等宽 spinner 替换文字

### 空状态

- 居中图标（灰色）+ "暂无数据" 标题 + 引导文案 + 行动按钮
- 每类数据空态都要有，不只是占位

### 页面级模式 🔴

#### 登录页 `/login`

- 居中卡片（420px 宽）+ 浅灰背景
- 品牌 logo 区（图标 + 平台名 + 副标题）
- 邮箱 + 密码表单 + "记住我"复选框
- "忘记密码"链接 + "注册新账号"链接
- 登录失败时 Toast 报错，不刷新页面
- 登录成功跳转 `/` 仪表盘

#### 仪表盘 `/`（首页）

- 顶部统计卡片行（6 张：活跃应用/Agent 数/知识库数/今日对话/响应时间/Token 用量）
- 左列：快捷操作按钮组（新建对话/Agent/知识库/工作流/Prompt）
- 右列：最近活动时间线（按时间倒序，彩色状态点区分模块）
- 数据来自各模块聚合查询

#### 用户管理 `/users`

- 用户列表表格：头像 + 用户名 / 邮箱 / 角色 / 状态 / 创建时间 / 操作
- 搜索栏 + 状态筛选下拉
- "新建用户"按钮 → 展开内联创建表单（用户名/邮箱/密码/角色）
- 操作列：编辑 / 禁用
- 管理员专属页面

#### Prompt 模板编辑器 `/prompt/[id]`

- 左右双栏布局：编辑区（左 60%）+ 变量面板和预览（右 40%）
- 编辑区：模板名称 + 模板内容（等宽字体 textarea）
- 变量面板：自动提取 `{{variable}}` 列表，标注变量类型和来源
- 变量类型：文本（手动填入）/ 上下文（自动注入如 chat_history）/ RAG（自动注入如 retrieved_docs）
- 实时预览：将已赋值的变量高亮替换入模板原文
- 保存按钮

#### 设置页 `/settings`

- 左侧竖直导航（个人信息 / 修改密码 / API 密钥 / 通知偏好）
- 右侧对应表单卡片
- 个人信息：头像上传区（虚线框 + hover 主色高亮）+ 用户名 + 邮箱 + 简介 + 保存按钮
- 修改密码：当前密码 + 新密码 + 确认新密码 + 更新按钮

## 页面路由清单 🔴

| 路由 | 页面 | 对应模块 |
|------|------|----------|
| `/login` | 登录页 | auth |
| `/` | 仪表盘（首页） | 聚合 |
| `/chat` | 对话应用列表 | chat |
| `/chat/[id]` | 对话详情 | chat |
| `/agent` | Agent 列表 | agent |
| `/agent/[id]` | Agent 配置/编辑 | agent |
| `/knowledge` | 知识库列表 | knowledge |
| `/knowledge/[id]` | 知识库详情/文档管理 | knowledge |
| `/workflow` | 工作流列表 | workflow |
| `/workflow/[id]` | 工作流编辑器 | workflow |
| `/prompt` | Prompt 模板列表 | prompt |
| `/prompt/[id]` | Prompt 编辑器 | prompt |
| `/provider` | 模型提供商状态 | provider |
| `/users` | 用户管理 | auth |
| `/settings` | 个人设置 | auth |

## 前端工程约束 🔴

### 技术栈

```
React + Next.js (App Router) + TypeScript
Tailwind CSS v4
Motion (motion/react)    ← 动效
@phosphor-icons/react    ← 图标
```

### 文件组织

```
frontend/src/
├── app/          # Next.js App Router 页面
├── components/   # 可复用组件
│   ├── ui/       # 基础 UI（Button/Card/Input/Table/Tag/Modal/Toast/Skeleton）
│   ├── chat/     # 对话组件
│   ├── workflow/ # 工作流画布
│   └── layout/   # 布局组件（Sidebar/Header）
├── hooks/        # 自定义 Hooks
├── lib/          # 工具函数 / API 客户端
└── types/        # TypeScript 类型定义
```

### 图标 🔴

- 统一使用 `@phosphor-icons/react`
- `strokeWidth: 1.5` 全局统一
- 禁止 emoji 作为结构性图标
- 禁止手绘 SVG 路径

### 状态覆盖 🔴

每个组件必须覆盖：**默认 → hover → active → focus → disabled → loading → empty → error** 八个状态。禁止只写 happy path。

### 无障碍底线 🔴

- 色对比 ≥ 4.5:1（正文）/ 3:1（大文字）
- 所有可交互元素有可见 focus ring
- icon-only 按钮有 `aria-label`
- 表格有 `aria-sort` 标识排序列
- Toast 使用 `aria-live="polite"`
- 动效尊重 `prefers-reduced-motion`

### 色彩一致性锁定 🔴

- 全局一个强调色（`--color-primary`），不出现第二个彩色 CTA
- 语义色仅用于状态指示（成功/警告/错误），不作装饰
- 不混用 warm gray 和 cool gray

### 禁止项（来自 design-taste-frontend §9）🔴

- 禁止 em-dash `—` 作为设计元素
- 禁止纯黑 `#000000`
- 禁止手绘 SVG 图标
- 禁止 `<div>` 拼凑的假产品截图
- 禁止三列等宽特征卡片
- 禁止占位符替代表单标签
- 禁止 scroll cue 文字（"向下滚动" 等）
