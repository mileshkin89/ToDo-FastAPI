from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from database import AsyncSessionLocal, engine


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    """Initialize the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close all database connections and dispose of the engine."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session as a generator."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database is not initialized")

    async with AsyncSessionLocal() as db:
        yield db


@asynccontextmanager
async def get_db_contextmanager() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session as a context manager. Used for testing."""
    if AsyncSessionLocal is None:
        raise RuntimeError("Database is not initialized")

    async with AsyncSessionLocal() as db:
        yield db


async def reset_db() -> None:
    """Reset the database by dropping and recreating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
