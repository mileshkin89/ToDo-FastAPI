import asyncio
from datetime import datetime
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app import app
from apps.auth.dependencies import get_current_user
from apps.auth.jwt import create_access_token
from database.db import close_db, get_db_contextmanager, reset_db
from database.models import Task, User
from infrastructure.redis.client import get_redis
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
    return CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")


class FakeRedis:
    """
    Lightweight Redis stub used in tests to replace the real Redis client.
    Provides only the minimal interface required by the application code.
    """

    def __init__(self):
        self._keys: set[str] = set()

    async def scan_iter(self, match: str | None = None, count: int = 100):
        if False:
            yield None

    async def delete(self, *keys):
        return len(keys)

    async def close(self):
        pass


@pytest.fixture(autouse=True)
def override_redis():
    """
    Automatically override the `get_redis` dependency with a fake Redis
    implementation for all tests, preventing access to a real Redis instance.
    """

    async def _get_fake_redis():
        yield FakeRedis()

    app.dependency_overrides[get_redis] = _get_fake_redis
    yield
    app.dependency_overrides.pop(get_redis, None)


@pytest.fixture
async def admin_user(db_session, pwd_context):
    user = User(
        email="admin@example.com",
        name="Admin",
        hashed_password=pwd_context.hash("admin"),
        is_active=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def override_admin(admin_user):
    async def _override():
        return admin_user

    app.dependency_overrides[get_current_user] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def another_user(db_session: AsyncSession, pwd_context: CryptContext) -> User:
    user = User(
        email="another@example.com",
        name="Another User",
        hashed_password=pwd_context.hash("anotherpassword"),
        is_active=True,
        is_superuser=False,
        registered_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
def another_access_token(another_user: User) -> str:
    data = {"sub": str(another_user.id)}
    return create_access_token(data)


@pytest.fixture
def admin_access_token(admin_user: User) -> str:
    data = {"sub": str(admin_user.id)}
    return create_access_token(data)
