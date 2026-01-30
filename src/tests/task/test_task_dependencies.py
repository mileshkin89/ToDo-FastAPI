import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.task.dependencies import (
    get_task_by_id,
    get_task_to_owner,
    get_task_to_owner_or_admin,
)
from database.models import Task, User


@pytest.mark.asyncio
async def test_get_task_by_id_success(
    db_session: AsyncSession,
    test_task: Task,
):
    task = await get_task_by_id(
        task_id=test_task.id,
        db=db_session,
    )

    assert task.id == test_task.id
    assert task.user_id == test_task.user_id
    assert task.title == test_task.title


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(
    db_session: AsyncSession,
):
    with pytest.raises(HTTPException) as exc:
        await get_task_by_id(
            task_id=999,
            db=db_session,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_get_task_to_owner_success(
    db_session: AsyncSession,
    test_user: User,
    test_task: Task,
):
    task = await get_task_to_owner(
        task_id=test_task.id,
        db=db_session,
        current_user=test_user,
    )

    assert task.id == test_task.id
    assert task.user_id == test_user.id


@pytest.mark.asyncio
async def test_get_task_to_owner_not_found(
    db_session: AsyncSession,
    test_user: User,
):
    with pytest.raises(HTTPException) as exc:
        await get_task_to_owner(
            task_id=999,
            db=db_session,
            current_user=test_user,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_task_to_owner_access_denied(
    db_session: AsyncSession,
    test_task: Task,
    pwd_context,
):
    other_user = User(
        email="other@example.com",
        name="Other User",
        hashed_password=pwd_context.hash("password"),
        is_active=True,
    )

    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    with pytest.raises(HTTPException) as exc:
        await get_task_to_owner(
            task_id=test_task.id,
            db=db_session,
            current_user=other_user,
        )

    assert exc.value.status_code == 403
    assert exc.value.detail == "Access denied"


@pytest.mark.asyncio
async def test_owner_or_admin_owner_success(
    db_session: AsyncSession,
    test_user: User,
    test_task: Task,
):
    task = await get_task_to_owner_or_admin(
        task_id=test_task.id,
        db=db_session,
        current_user=test_user,
    )

    assert task.id == test_task.id


@pytest.mark.asyncio
async def test_owner_or_admin_admin_success(
    db_session: AsyncSession,
    test_task: Task,
    pwd_context,
):
    admin = User(
        email="admin@example.com",
        name="Admin",
        hashed_password=pwd_context.hash("admin"),
        is_active=True,
        is_superuser=True,
    )

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    task = await get_task_to_owner_or_admin(
        task_id=test_task.id,
        db=db_session,
        current_user=admin,
    )

    assert task.id == test_task.id


@pytest.mark.asyncio
async def test_owner_or_admin_access_denied(
    db_session: AsyncSession,
    test_task: Task,
    pwd_context,
):
    user = User(
        email="user@example.com",
        name="User",
        hashed_password=pwd_context.hash("password"),
        is_active=True,
        is_superuser=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    with pytest.raises(HTTPException) as exc:
        await get_task_to_owner_or_admin(
            task_id=test_task.id,
            db=db_session,
            current_user=user,
        )

    assert exc.value.status_code == 403
