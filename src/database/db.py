from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from ..settings import settings

engine: AsyncEngine | None = None
AsyncSessionLocal: sessionmaker | None = None


class Base(DeclarativeBase):
    pass


def init_engine() -> None:
    global engine, AsyncSessionLocal

    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        engine = create_async_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=True,
        )
    else:
        engine = create_async_engine(
            db_url,
            echo=True,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
        )

    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# Database dependencies
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db


async def reset_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
