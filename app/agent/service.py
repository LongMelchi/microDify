"""Agent module service layer.

Pure async business logic. Never receives Request/Response/BackgroundTasks objects.
Signature only accepts db session, user context, and business parameters.

Dependency whitelist: core/, auth/, provider/, rag/, prompt/
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def get_agent(
    db: AsyncSession,
    user_id: UUID,
    agent_id: UUID,
) -> dict:
    """获取 Agent 配置详情。

    Args:
        db: 数据库会话。
        user_id: 请求用户 ID。
        agent_id: Agent ID。

    Returns:
        Agent 配置字典。
    """
    # TODO: Load agent from DB → validate ownership → return serialized
    raise NotImplementedError("get_agent not yet implemented")


async def create_agent(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    system_prompt: str,
    model_provider: str,
    model_name: str,
    description: str | None = None,
    enabled_tools: list[str] | None = None,
    knowledge_base_ids: list[UUID] | None = None,
    prompt_template_id: UUID | None = None,
) -> UUID:
    """创建 Agent 配置。

    Args:
        db: 数据库会话。
        user_id: 所有者用户 ID。
        name: Agent 名称。
        system_prompt: 系统指令。
        model_provider: 模型提供商（如 "openai", "anthropic"）。
        model_name: 模型名称（如 "gpt-4o", "claude-sonnet-4"）。
        description: 可选描述。
        enabled_tools: 启用的预定义工具名数组，如 ["calculator", "web_search"]。
        knowledge_base_ids: 可选关联知识库 ID 列表。
        prompt_template_id: 可选绑定的 Prompt 模板 ID。

    Returns:
        新创建 Agent 的 UUID。
    """
    # TODO: Validate prompt_template_id exists via prompt service (by ID)
    # TODO: Validate knowledge_base_ids exist via knowledge service (by ID)
    # TODO: Validate enabled_tools are in the allowed predefined-tool list
    # TODO: Create Agent (+ M:N links in agent_knowledge_bases); store enabled_tools JSON
    ...
    raise NotImplementedError("create_agent not yet implemented")


async def run_agent(
    db: AsyncSession,
    user_id: UUID,
    agent_id: UUID,
    input: str,
) -> UUID:
    """执行 Agent 的 ReAct 推理循环。

    加载 Agent 配置，执行 ReAct 推理（思考→行动→观察循环），
    可选调用知识库检索和外部工具，SSE 流式返回推理过程，
    最终将结果持久化到 agent_executions。

    Args:
        db: 数据库会话。
        user_id: 请求用户 ID。
        agent_id: 目标 Agent ID。
        input: 用户输入文本。

    Returns:
        创建的 AgentExecution 记录 UUID。
    """
    # TODO: Load agent with knowledge_bindings and tool config
    # TODO: Build system prompt (interpolate prompt template if bound)
    # TODO: Initialize ReAct loop — max iterations, message history
    # TODO: Iterate: LLM thinks → tool call / knowledge retrieval → observe
    # TODO: On each iteration, yield reasoning step via SSE
    # TODO: When LLM produces final answer, exit loop
    # TODO: Persist AgentExecution with input, output, reasoning_steps, status
    # TODO: Track token usage
    ...
    raise NotImplementedError("run_agent not yet implemented")
