"""microDify — FastAPI application assembly.

Start the dev server::

    uvicorn app.main:app --reload
"""

import structlog
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import BizException, ErrorCode
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware, mark_started, get_metrics
from app.core.schemas import Result

# ── Module routers ──────────────────────────────────────────────────────────
# core/      — no router to mount (infrastructure only)
# common/    — not mounted (internal utilities, not an API surface)
# provider/  — not mounted (internal LLM adapter, config via env vars)

from app.auth import router as auth_router
from app.provider import router as provider_router
from app.prompt import router as prompt_router
from app.knowledge import router as knowledge_router
from app.chat import router as chat_router
from app.agent import router as agent_router
from app.workflow import router as workflow_router

settings = get_settings()

# Must be called before any structlog.get_logger() — configures the global logger.
setup_logging(debug=settings.debug)

logger = structlog.get_logger("microdify")


# ── Lifecycle ───────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle hooks."""
    mark_started()
    logger.info(
        "Starting %s — environment: %s",
        settings.app_name,
        "debug" if settings.debug else "production",
    )
    # ── startup ──────────────────────────────────────────────────────────
    from app.provider import ProviderRegistry, LLMGateway
    from app.provider.openai_provider import OpenAIProvider
    from app.provider.anthropic_provider import AnthropicProvider

    registry = ProviderRegistry()
    if settings.openai_api_key:
        openai_p = OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
        )
        registry.register_llm("openai", openai_p)
        registry.register_embedding("openai", openai_p)
        logger.info(
            "Registered OpenAI provider base_url=%s",
            settings.openai_base_url or "https://api.openai.com",
        )
    if settings.anthropic_api_key:
        registry.register_llm(
            "anthropic",
            AnthropicProvider(
                api_key=settings.anthropic_api_key,
                base_url=settings.anthropic_base_url or None,
            ),
        )
        logger.info(
            "Registered Anthropic provider base_url=%s",
            settings.anthropic_base_url or "https://api.anthropic.com",
        )

    app.state.gateway = LLMGateway(registry)  # type: ignore[attr-defined]

    yield

    # ── shutdown ──────────────────────────────────────────────────────────
    logger.info("Shutting down %s", settings.app_name)
    await engine.dispose()


# ── Application ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)


# ── Middleware ──────────────────────────────────────────────────────────────

# A wildcard origin ("*") and credentialed requests are mutually exclusive per
# the CORS spec — browsers reject "*" when credentials are sent. Only allow
# credentials when explicit origins are configured.
_allow_credentials = "*" not in settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)


# ── Routers ─────────────────────────────────────────────────────────────────
# Each router declares its own ``prefix`` — do NOT pass prefix here.

app.include_router(auth_router)
app.include_router(provider_router)
app.include_router(prompt_router)
app.include_router(knowledge_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(workflow_router)


# ── Health check ────────────────────────────────────────────────────────────


@app.get("/health", tags=["infra"])
async def health() -> dict:
    """Health check + runtime metrics."""
    return Result.ok(
        {
            "app": settings.app_name,
            "version": "0.1.0",
            "metrics": get_metrics(),
        }
    ).model_dump()


# ── Global exception handlers ───────────────────────────────────────────────


@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    """Translate ``BizException`` into a ``Result.fail()`` response."""
    return JSONResponse(
        status_code=exc.code,
        content=Result.fail(exc.code, exc.message).model_dump(),
    )


def _format_validation_errors(exc) -> str:
    """Flatten pydantic/FastAPI validation errors into a single message."""
    errors: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(part) for part in err["loc"])
        errors.append(f"{loc}: {err['msg']}")
    return "; ".join(errors)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI request body/query validation failures with unified Result."""
    return JSONResponse(
        status_code=ErrorCode.BAD_REQUEST.value[0],
        content=Result.fail(ErrorCode.BAD_REQUEST.value[0], _format_validation_errors(exc)).model_dump(),
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic ``ValidationError`` raised inside service-layer logic."""
    return JSONResponse(
        status_code=ErrorCode.BAD_REQUEST.value[0],
        content=Result.fail(ErrorCode.BAD_REQUEST.value[0], _format_validation_errors(exc)).model_dump(),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ``ValueError`` raised from business logic as 400."""
    return JSONResponse(
        status_code=400,
        content=Result.fail(ErrorCode.BAD_REQUEST.value[0], str(exc)).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions — returns a 500."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=ErrorCode.INTERNAL_ERROR.value[0],
        content=Result.fail(
            ErrorCode.INTERNAL_ERROR.value[0],
            ErrorCode.INTERNAL_ERROR.value[1],
        ).model_dump(),
    )


# ── CLI entry point ─────────────────────────────────────────────────────────


def main() -> None:
    """Run the application via ``python -m app.main`` or the ``microdify`` CLI."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
