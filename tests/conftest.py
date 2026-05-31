"""Pytest fixtures for microDify tests."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# Use a test database — override the DATABASE_URL for the test session
TEST_DATABASE_URL = settings.database_url + "_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio for async tests."""
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, Any]:
    """Create all tables before tests and drop them after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(setup_database: Any) -> AsyncGenerator[AsyncSession, Any]:
    """Provide a clean database session for each test."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, Any]:
    """Provide an HTTP client that uses the test database session."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, Any]:
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
