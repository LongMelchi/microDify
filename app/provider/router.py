"""Provider debug routes — verify gateway status and test LLM calls."""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.deps import get_gateway
from app.core.schemas import Result

settings = get_settings()
router = APIRouter(
    prefix="/provider",
    tags=["provider"],
)


class TestChatRequest(BaseModel):
    provider: str = Field(default="openai", description="Provider name: openai | anthropic")
    model: str = Field(default="", description="Model name, defaults to settings.DEFAULT_LLM_MODEL")
    message: str = Field(default="hi", description="Test message")


@router.get("/status")
async def provider_status(request: Request):
    """Return registered providers and their API key status."""
    gw = request.app.state.gateway
    return Result.ok(
        {
            "llm_providers": gw.available_llm,
            "embedding_providers": gw.available_embedding,
        }
    ).model_dump()


@router.post("/test-chat")
async def provider_test_chat(
    body: TestChatRequest,
    gw=Depends(get_gateway),
):
    """Send a single test message and return the response (non-streaming)."""
    model = body.model or settings.default_llm_model
    response = await gw.chat(body.provider, model, [{"role": "user", "content": body.message}])
    return Result.ok({"response": response}).model_dump()
