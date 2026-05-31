"""Chat module service layer.

Pure async business logic. Never receives Request/Response/BackgroundTasks objects.
Signature only accepts db session, user context, and business parameters.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.chat.models import ChatApp, ChatAppKnowledgeBase, Conversation, Message


async def create_chat_app(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    description: str | None = None,
    prompt_template_id: UUID | None = None,
    knowledge_base_ids: list[UUID] | None = None,
) -> ChatApp:
    """Create a new chat application.

    Args:
        db: Database session.
        user_id: Owner user ID.
        name: Chat app name.
        description: Optional description.
        prompt_template_id: Optional bound prompt template ID.
        knowledge_base_ids: Optional list of knowledge base IDs to associate.

    Returns:
        The created ChatApp instance.
    """
    # TODO: Validate prompt_template_id exists via prompt service (by ID)
    # TODO: Validate knowledge_base_ids exist via knowledge service (by ID)

    chat_app = ChatApp(
        name=name,
        description=description,
        prompt_template_id=prompt_template_id,
        user_id=user_id,
    )
    db.add(chat_app)
    await db.flush()  # Get chat_app.id before adding M:N links

    if knowledge_base_ids:
        for kb_id in knowledge_base_ids:
            link = ChatAppKnowledgeBase(
                chat_app_id=chat_app.id,
                knowledge_base_id=kb_id,
            )
            db.add(link)

    await db.commit()
    await db.refresh(chat_app)
    return chat_app


async def run_chat(
    db: AsyncSession,
    user_id: UUID,
    chat_app_id: UUID,
    conversation_id: UUID | None = None,
    message: str | None = None,
) -> None:
    """Execute a streaming chat conversation.

    Creates or continues a conversation, persists the user message,
    triggers LLM inference via provider gateway, and streams tokens
    back through SSE.

    Args:
        db: Database session.
        user_id: Requesting user ID.
        chat_app_id: Target chat application ID.
        conversation_id: Existing conversation ID, or None to create a new one.
        message: User message content.
    """
    # TODO: Load chat_app with its prompt_template and knowledge_bindings
    # TODO: Create or retrieve conversation
    # TODO: Persist user message
    # TODO: Retrieve message history for context
    # TODO: Invoke LLMGateway (via provider/) with prompt interpolation
    # TODO: Stream response tokens via SSE generator
    # TODO: Persist assistant response message on completion
    raise NotImplementedError("run_chat not yet implemented")
