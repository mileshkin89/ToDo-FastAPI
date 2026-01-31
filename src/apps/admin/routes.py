from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from apps.admin.dependencies import superuser_required
from apps.auth.dependencies import get_user_by_id
from apps.schemas import TaskByUserResponse, UserListResponse, UserResponse
from database.db import get_db
from database.models import Task, User

admin_router = APIRouter()


@admin_router.get(
    "/users",
    dependencies=[Depends(superuser_required)],
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get list of users",
    description="Retrieve a paginated list of all users. Requires superuser privileges. Supports filtering by active status, searching by name or email, and sorting.",
    response_description="List of users with pagination metadata"
)
async def get_users(
        db: AsyncSession = Depends(get_db),
        active: bool | None = Query(None, description="Filter by user active status"),
        q: str | None = Query(None, description="Search by name or email"),
        skip: int = Query(0, ge=0, description="Skip N records"),
        limit: int = Query(10, ge=1, le=100, description="Record limit"),
        sort_by: str = Query("registered_at", description="Sorting field",
                             examples=["registered_at", "last_login", "id"]),
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sorting order"),
):
    # Base request
    base_stmt = select(User)

    # Filter by status
    if active is not None:
        base_stmt = base_stmt.where(User.is_active.is_(active))

    # Search
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        base_stmt = base_stmt.where(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    # Sorting
    sortable_fields = {
        "registered_at": User.registered_at,
        "last_login": User.last_login,
        "id": User.id,
    }

    field = sortable_fields.get(sort_by)
    if not field:
        raise HTTPException(status_code=400, detail=f"Cannot sort by '{sort_by}'")

    base_stmt = base_stmt.order_by(
        field.desc() if sort_order == "desc" else field.asc()
    )

    # Count
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = await db.scalar(count_stmt)

    # Pagination
    data_stmt = base_stmt.offset(skip).limit(limit)
    result = await db.execute(data_stmt)
    users = result.scalars().all()

    return UserListResponse(
        users=users,
        pagination={
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + len(users) < total,
        },
    )


@admin_router.get(
    "/users/{user_id}",
    dependencies=[Depends(superuser_required)],
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve detailed information about a specific user by their ID. Requires superuser privileges.",
    response_description="User details"
)
async def get_user(
        user: User | None = Depends(get_user_by_id),
):
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@admin_router.patch(
    "/users/{user_id}/deactivate",
    dependencies=[Depends(superuser_required)],
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user",
    description="Deactivate a user account by setting is_active to False. Requires superuser privileges.",
    response_description="Updated user information"
)
async def deactivate_user(
        user: User | None = Depends(get_user_by_id),
        db: AsyncSession = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()

    return user


@admin_router.patch(
    "/users/{user_id}/activate",
    dependencies=[Depends(superuser_required)],
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate user",
    description="Activate a user account by setting is_active to True. Requires superuser privileges.",
    response_description="Updated user information"
)
async def activate_user(
        user: User | None = Depends(get_user_by_id),
        db: AsyncSession = Depends(get_db)
):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()

    return user


@admin_router.get(
    "/users/{user_id}/tasks",
    dependencies=[Depends(superuser_required)],
    response_model=TaskByUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get tasks by user",
    description="Retrieve all tasks belonging to a specific user. Requires superuser privileges. Supports filtering by completion status, searching, and sorting.",
    response_description="User information with their tasks and pagination metadata"
)
async def get_tasks_by_user(
        user_id: int = Path(...),
        user: User | None = Depends(get_user_by_id),
        db: AsyncSession = Depends(get_db),
        completed: bool | None = Query(None, description="Filter by execution status"),
        q: str | None = Query(None, description="Search by task title or description"),
        skip: int = Query(0, ge=0, description="Skip N records"),
        limit: int = Query(10, ge=1, le=100, description="Record limit"),
        sort_by: str = Query("created_at", description="Sorting field",
                             examples=["created_at", "start_at", "completed_at", "due_date", "id"]),
        sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sorting order"),
):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    base_stmt = select(Task).where(Task.user_id == user_id)

    # Filter by status
    if completed is not None:
        base_stmt = base_stmt.where(Task.completed.is_(completed))

    # Search
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        base_stmt = base_stmt.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Sorting
    sortable_fields = {
        "created_at": Task.created_at,
        "start_at": Task.start_at,
        "completed_at": Task.completed_at,
        "due_date": Task.due_date,
        "id": Task.id,
    }

    field = sortable_fields.get(sort_by)
    if not field:
        raise HTTPException(status_code=400, detail=f"Cannot sort by '{sort_by}'")

    base_stmt = base_stmt.order_by(
        field.desc() if sort_order == "desc" else field.asc()
    )

    # Count
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = await db.scalar(count_stmt)

    # Pagination
    data_stmt = base_stmt.offset(skip).limit(limit)
    result = await db.execute(data_stmt)
    tasks = result.scalars().all()

    return TaskByUserResponse(
        user=user,
        tasks=tasks,
        pagination={
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + len(tasks) < total,
        },
    )