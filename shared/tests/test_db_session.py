"""Tests for database session management."""

import pytest
from sqlalchemy import text

from shared.db.session import create_engine, create_session_factory, get_session


@pytest.mark.asyncio
async def test_create_engine():
    """Test engine creation."""
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    assert engine is not None
    await engine.dispose()


@pytest.mark.asyncio
async def test_session_context_manager():
    """Test session context manager."""
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    session_factory = create_session_factory(engine)

    async with get_session(session_factory) as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    await engine.dispose()
