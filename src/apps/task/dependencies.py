from fastapi import Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dependencies import get_current_user
from database.db import get_db
from database.models import Task, User


async def get_task_by_id(
        task_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
) -> Task:
    """Get a task by ID or raise 404 if not found."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


async def get_task_to_owner(
        task_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Task:
    """Get a task by ID, ensuring the current user is the owner."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return task


async def get_task_to_owner_or_admin(
    task_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """Get a task by ID, ensuring the current user is the owner or an admin."""
    stmt = select(Task).where(Task.id == task_id)
    result = await db.execute(stmt)
    task = result.scalars().one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if not (
        task.user_id == current_user.id
        or current_user.is_superuser
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return task