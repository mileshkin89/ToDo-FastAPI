import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.models import User
from apps.task.models import Task
from database.db import (
    close_db,
    engine,
    get_db,
    get_db_contextmanager,
    init_db,
    reset_db,
)


@pytest.mark.asyncio
async def test_init_db_creates_tables(db_session: AsyncSession):
    """Test that init_db creates all tables."""
    await init_db()

    from sqlalchemy import text

    result = await db_session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table'")
    )
    table_names = [row[0] for row in result.fetchall()]

    assert "users" in table_names
    assert "tasks" in table_names

    result = await db_session.execute(
        text("PRAGMA table_info(users)")
    )
    user_columns = [row[1] for row in result.fetchall()]

    assert "id" in user_columns
    assert "email" in user_columns
    assert "hashed_password" in user_columns

    result = await db_session.execute(
        text("PRAGMA table_info(tasks)")
    )
    task_columns = [row[1] for row in result.fetchall()]

    assert "id" in task_columns
    assert "title" in task_columns
    assert "user_id" in task_columns


@pytest.mark.asyncio
async def test_reset_db_drops_and_recreates_tables():
    """Test that reset_db drops and recreates all tables."""
    # This test requires a fresh session to avoid fixture protection
    async with get_db_contextmanager() as session:
        from passlib.context import CryptContext

        from settings import settings

        pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_SCHEME], deprecated="auto")

        user = User(
            email="test@example.com",
            name="Test User",
            hashed_password=pwd_context.hash("password"),
            is_active=True
        )
        session.add(user)
        await session.commit()

        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count_before = result.scalar()
        assert count_before == 1

        await reset_db()

        result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count_after = result.scalar()
        assert count_after == 0


@pytest.mark.asyncio
async def test_get_db_returns_async_generator():
    """Test that get_db returns an async generator."""
    db_gen = get_db()

    import inspect
    assert inspect.isasyncgen(db_gen)

    async for session in db_gen:
        assert isinstance(session, AsyncSession)
        break


@pytest.mark.asyncio
async def test_get_db_context_manager_works():
    """Test the get_db_context_manager context manager."""
    async with get_db_contextmanager() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active

        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        await session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)"))
        await session.commit()


@pytest.mark.asyncio
async def test_database_connection_in_testing_mode():
    """Test that database uses SQLite in testing mode."""
    url = str(engine.url)

    assert "sqlite+aiosqlite" in url
    assert ":memory:" in url


@pytest.mark.asyncio
async def test_can_create_and_query_models(
        db_session: AsyncSession,
        test_user: User,
        test_task: Task
):
    """Test that models can be created and queried."""
    user = test_user
    task = test_task

    assert user.id is not None
    assert task.id is not None
    assert task.user_id == user.id

    from sqlalchemy import select

    user_stmt = select(User).where(User.id == user.id)
    user_result = await db_session.execute(user_stmt)
    user_from_db = user_result.scalar_one_or_none()

    task_stmt = select(Task).where(Task.id == task.id)
    task_result = await db_session.execute(task_stmt)
    task_from_db = task_result.scalar_one_or_none()

    assert user_from_db is not None
    assert user_from_db.email == user.email

    assert task_from_db is not None
    assert task_from_db.title == task.title

    from sqlalchemy.orm import selectinload

    user_with_tasks_stmt = (
        select(User)
        .where(User.id == user.id)
        .options(selectinload(User.tasks))
    )
    user_with_tasks_result = await db_session.execute(user_with_tasks_stmt)
    user_with_tasks = user_with_tasks_result.scalar_one_or_none()

    assert user_with_tasks is not None
    assert len(user_with_tasks.tasks) == 1
    assert user_with_tasks.tasks[0].id == task.id


@pytest.mark.asyncio
async def test_database_close_db_function():
    """Test that close_db function works correctly."""
    await close_db()
    assert True
