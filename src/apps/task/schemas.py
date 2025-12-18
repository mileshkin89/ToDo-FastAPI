from datetime import datetime

from pydantic import BaseModel, Field

from apps.auth.schemas import UserResponse


class TaskCreate(BaseModel):
    title: str = Field(max_length=150)
    description: str | None = Field(default=None, max_length=500)
    completed: bool = Field(default=False)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=150)
    description: str | None = Field(default=None, max_length=500)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime

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
