from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from database.db import get_db

from .dependencies import get_task_by_id
from .models import Task
from .schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate

task_router = APIRouter()


@task_router.get("/tasks", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
async def task_list(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        completed: bool | None = Query(None, description="Filter by execution status"),
        q: str | None = Query(None, description="Search by task title"),
        skip: int = Query(0, ge=0, description="Skip N records"),
        limit: int = Query(10, ge=1, le=100, description="Record limit"),
        sort_by: str = Query("created_at", description="Sorting field"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sorting order"),
):
    # Base request
    stmt = select(Task).where(Task.user_id == current_user.id)

    # Filter by status
    if completed is not None:
        stmt = stmt.where(Task.completed == completed)

    # Search
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Sorting
    order_column = getattr(Task, sort_by, Task.created_at)
    if sort_order == "desc":
        stmt = stmt.order_by(order_column.desc())
    else:
        stmt = stmt.order_by(order_column.asc())

    # Pagination
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    total = len(tasks)

    return TaskListResponse(
        tasks=tasks,
        pagination={
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + len(tasks)) < total
        }
    )


@task_router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        task: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task_db = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )

    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)

    return task_db


@task_router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def read_task(
        task: Task = Depends(get_task_by_id),
):
    return task


@task_router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task(
        task_up: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_by_id),
):
    if task_up.title is not None:
        task.title = task_up.title
    if task_up.description is not None:
        task.description = task_up.description

    if task_up.title is not None or task_up.description is not None:
        task.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(task)

    return task


@task_router.patch("/tasks/{task_id}/toggle", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def toggle_task(
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_by_id),
):
    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(task)

    return task


@task_router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_by_id),
):
    await db.delete(task)
    await db.commit()
