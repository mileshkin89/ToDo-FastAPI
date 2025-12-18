from fastapi import Path, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from apps.task.models import Task
from database.db import get_db


async def get_task_by_id(
        task_id: int = Path(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Task:
    stmt = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )
    result = await db.execute(stmt)
    task = result.scalars().one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task