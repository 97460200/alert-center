"""FastAPI dependencies."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import create_engine, create_session_factory, get_session

from app.config import settings

_engine = create_engine(settings.database_url)
_session_factory = create_session_factory(_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session(_session_factory):
        yield session
