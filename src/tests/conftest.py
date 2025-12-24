import asyncio
from datetime import datetime
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from apps.auth.jwt import create_access_token
from apps.auth.models import User
from apps.task.models import Task
from database.db import close_db, get_db_contextmanager, reset_db
from settings import settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_database():
    """
    Reset the SQLite database before each test.

    This fixture ensures that the database is cleared and recreated for every test function.
    It helps maintain test isolation by preventing data leakage between tests.
    """
    await reset_db()
    yield
    await close_db()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Provide an async database session for database interactions.

    This fixture yields an async session using `get_db_contextmanager`, ensuring that the session
    is properly closed after each test.
    """
    async with get_db_contextmanager() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client():
    """Provide an asynchronous test client for making HTTP requests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client
        await async_client.aclose()


@pytest.fixture
async def test_user(db_session: AsyncSession, pwd_context: CryptContext) -> User:
    """Create and return a test user."""
    hashed_password = pwd_context.hash("testpassword123")

    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
        registered_at=datetime.utcnow()
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: User) -> Task:
    """Create and return a test task."""
    task = Task(
        title="Test Task",
        description="Test task description",
        completed=False,
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return task


@pytest.fixture
def valid_access_token(test_user: User) -> str:
    """Generate a valid access token for testing."""
    data = {"sub": str(test_user.id)}
    return create_access_token(data)


@pytest.fixture
def pwd_context():
    """Get the password hashing context."""
    return CryptContext(schemes=[settings.CRYPT_CONTEXT], deprecated="auto")



