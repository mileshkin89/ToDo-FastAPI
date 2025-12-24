from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from settings import settings

async_db_url = settings.database_url

if async_db_url.startswith("sqlite"):
    engine: AsyncEngine = create_async_engine(
        async_db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine: AsyncEngine = create_async_engine(
        async_db_url,
        echo=True,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
    )

AsyncSessionLocal: sessionmaker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

sync_db_url = async_db_url.replace("postgresql+asyncpg", "postgresql")
sync_postgresql_engine: Engine = create_engine(sync_db_url, echo=False)
