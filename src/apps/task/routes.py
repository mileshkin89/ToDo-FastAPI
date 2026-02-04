from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.analytics.cache import AnalyticsCacheInvalidator
from apps.analytics.dependencies import get_cache_invalidator
from apps.auth.dependencies import active_user_required, get_current_user
from apps.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from database.db import get_db
from database.models import Task, User

from .dependencies import get_task_to_owner, get_task_to_owner_or_admin

task_router = APIRouter()


@task_router.get(
    "/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's tasks",
    description="Retrieve a paginated list of tasks belonging to the authenticated user. Supports filtering by completion status, searching by title or description, and sorting.",
    response_description="List of tasks with pagination metadata"
)
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

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt)

    # Pagination
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=tasks,
        pagination={
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + len(tasks)) < total
        }
    )


@task_router.post(
    "/tasks",
    dependencies=[Depends(active_user_required)],
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
    description="Create a new task for the authenticated user. The task is automatically associated with the current user. Invalidates user analytics cache.",
    response_description="Created task information"
)
async def create_task(
        task: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        cache_invalidator: AnalyticsCacheInvalidator = Depends(get_cache_invalidator),
):
    task_db = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id,
        start_at=task.start_at,
        due_date=task.due_date,
    )

    db.add(task_db)
    await db.commit()
    await db.refresh(task_db)

    await cache_invalidator.invalidate_user(task_db.user_id)

    return task_db


@task_router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task by ID",
    description="Retrieve detailed information about a specific task. Users can only access their own tasks, while admins can access any task.",
    response_description="Task details"
)
async def read_task(
        task: Task = Depends(get_task_to_owner_or_admin),
):
    return task


@task_router.put(
    "/tasks/{task_id}",
    dependencies=[Depends(active_user_required)],
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update task",
    description="Update an existing task. Only the task owner or an admin can update a task. Only provided fields will be updated. Invalidates user analytics cache.",
    response_description="Updated task information"
)
async def update_task(
        task_up: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_to_owner_or_admin),
        cache_invalidator: AnalyticsCacheInvalidator = Depends(get_cache_invalidator),
):
    update_data = task_up.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    if update_data:
        task.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(task)
        await cache_invalidator.invalidate_user(task.user_id)

    return task


@task_router.patch(
    "/tasks/{task_id}/toggle",
    dependencies=[Depends(active_user_required)],
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggle the completion status of a task. If marking as completed, sets completed_at timestamp. Only the task owner or an admin can toggle a task. Invalidates user analytics cache.",
    response_description="Updated task with new completion status"
)
async def toggle_task(
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_to_owner_or_admin),
        cache_invalidator: AnalyticsCacheInvalidator = Depends(get_cache_invalidator),
):
    task.completed = not task.completed
    task.completed_at = datetime.utcnow() if task.completed else None
    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    await cache_invalidator.invalidate_user(task.user_id)

    return task


@task_router.delete(
    "/tasks/{task_id}",
    dependencies=[Depends(active_user_required)],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
    description="Delete a task. Only the task owner can delete their tasks. Admins cannot delete tasks belonging to other users. Invalidates user analytics cache.",
    response_description="No content on successful deletion"
)
async def delete_task(
        db: AsyncSession = Depends(get_db),
        task: Task = Depends(get_task_to_owner),
        cache_invalidator: AnalyticsCacheInvalidator = Depends(get_cache_invalidator),
):
    await db.delete(task)
    await db.commit()

    await cache_invalidator.invalidate_user(task.user_id)
