from datetime import datetime

from pydantic import BaseModel, Field

from apps.auth.schemas import UserResponse


class TaskCreate(BaseModel):
    title: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=500)
    completed: bool = Field(default=False)
    start_at: datetime | None = Field(default=None)
    due_date: datetime | None = Field(default=None)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    start_at: datetime | None = Field(default=None)
    due_date: datetime | None = Field(default=None)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    start_at: datetime | None
    completed_at: datetime | None
    due_date: datetime | None

    user: UserResponse | None

    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    pagination: dict | None = None

    model_config = {
        "from_attributes": True
    }
