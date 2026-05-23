"""Database session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool


def create_engine(database_url: str, **kwargs: Any) -> AsyncEngine:
    """Create async database engine."""
    default_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "echo": False,
    }
    if "pool_size" not in kwargs:
        default_kwargs["poolclass"] = NullPool

    return create_async_engine(database_url, **{**default_kwargs, **kwargs})


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
