import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.auth.models import User
from apps.task.dependencies import get_task_by_id
from apps.task.models import Task


@pytest.mark.asyncio
async def test_get_task_by_id_success(
        db_session: AsyncSession,
        test_user: User,
        test_task: Task,
):
    """
    Ensure a user can retrieve their own task by ID.
    """
    task = await get_task_by_id(
        task_id=test_task.id,
        db=db_session,
        current_user=test_user,
    )

    assert task.id == test_task.id
    assert task.user_id == test_user.id
    assert task.title == test_task.title


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(
        db_session: AsyncSession,
        test_user: User,
):
    """
    Ensure 404 is raised when the task does not exist.
    """
    with pytest.raises(HTTPException) as exc:
        await get_task_by_id(
            task_id=999,
            db=db_session,
            current_user=test_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_get_task_by_id_another_user(
        db_session: AsyncSession,
        test_task: Task,
        pwd_context,
):
    """
    Ensure a user cannot access another user's task.
    """
    other_user = User(
        email="other@example.com",
        name="Other User",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
    )

    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    with pytest.raises(HTTPException) as exc:
        await get_task_by_id(
            task_id=test_task.id,
            db=db_session,
            current_user=other_user,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Task not found"
