from datetime import date, datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field, model_validator


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=100)
    name: str | None = Field(default=None, max_length=50)
    password: str = Field(min_length=5, max_length=100)
    repeat_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    is_active: bool
    last_login: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    users: list[UserResponse]
    pagination: dict | None = None

    model_config = {
        "from_attributes": True
    }


class TaskByUserResponse(BaseModel):
    user: UserResponse
    pagination: dict | None = None
    tasks: list["TaskResponse"]

    model_config = {
        "from_attributes": True
    }


# Task Schemas
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

    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    pagination: dict | None = None

    model_config = {
        "from_attributes": True
    }


# Analytic Schemas
class CountersSchema(BaseModel):
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_users: int


class TaskLast24HoursSchema(BaseModel):
    day: datetime
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int


class TaskLastDaySchema(BaseModel):
    data: List[TaskLast24HoursSchema]


class TaskPerDaySchema(BaseModel):
    day: date
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int


class TaskLast7DaysSchema(BaseModel):
    data: List[TaskPerDaySchema]


class TaskPerWeekSchema(BaseModel):
    day: date
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int


class TaskLastMonthSchema(BaseModel):
    data: List[TaskPerWeekSchema]


class UserCountersSchema(BaseModel):
    user_id: int
    total_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    overdue_percent: float


class UserTaskLast24HoursSchema(BaseModel):
    user_id: int
    day: datetime
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    overdue_percent: float


class UserTaskLastDaySchema(BaseModel):
    data: List[UserTaskLast24HoursSchema]


class UserTaskPerDaySchema(BaseModel):
    user_id: int
    day: date
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    overdue_percent: float


class UserTaskLast7DaysSchema(BaseModel):
    data: List[UserTaskPerDaySchema]


class UserTaskPerWeekSchema(BaseModel):
    user_id: int
    day: date
    created_tasks: int
    active_tasks: int
    completed_tasks: int
    overdue_tasks: int
    overdue_percent: float


class UserTaskLastMonthSchema(BaseModel):
    data: List[UserTaskPerWeekSchema]