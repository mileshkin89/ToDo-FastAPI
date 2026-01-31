from datetime import date, datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field, model_validator


# Auth Schemas
class Token(BaseModel):
    """JWT token response schema."""
    access_token: str = Field(description="JWT access token for authentication")
    token_type: str = Field(description="Token type, typically 'bearer'")


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(max_length=100, description="User email address (must be unique)")
    name: str | None = Field(default=None, max_length=50, description="User's full name (optional)")
    password: str = Field(min_length=5, max_length=100, description="User password (minimum 5 characters)")
    repeat_password: str = Field(description="Password confirmation (must match password)")

    @model_validator(mode="after")
    def passwords_match(self):
        """Validate that password and repeat_password match."""
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    """Schema for user information response."""
    id: int = Field(description="Unique user identifier")
    email: EmailStr = Field(description="User email address")
    name: str | None = Field(default=None, description="User's full name")
    is_active: bool = Field(description="Whether the user account is active")
    last_login: datetime | None = Field(default=None, description="Timestamp of last login")

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    users: list[UserResponse] = Field(description="List of users")
    pagination: dict | None = Field(default=None, description="Pagination metadata (total, skip, limit, has_more)")

    model_config = {
        "from_attributes": True
    }


class TaskByUserResponse(BaseModel):
    """Schema for user tasks response with user information."""
    user: UserResponse = Field(description="User information")
    pagination: dict | None = Field(default=None, description="Pagination metadata (total, skip, limit, has_more)")
    tasks: list["TaskResponse"] = Field(description="List of tasks belonging to the user")

    model_config = {
        "from_attributes": True
    }


# Task Schemas
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(max_length=150, description="Task title (max 150 characters)")
    description: str | None = Field(default=None, max_length=500, description="Task description (optional, max 500 characters)")
    completed: bool = Field(default=False, description="Task completion status (default: false)")
    start_at: datetime | None = Field(default=None, description="Task start date and time (optional)")
    due_date: datetime | None = Field(default=None, description="Task due date and time (optional)")


class TaskUpdate(BaseModel):
    """Schema for updating an existing task. All fields are optional."""
    title: str | None = Field(default=None, max_length=150, description="Task title (optional, max 150 characters)")
    description: str | None = Field(default=None, max_length=500, description="Task description (optional, max 500 characters)")
    start_at: datetime | None = Field(default=None, description="Task start date and time (optional)")
    due_date: datetime | None = Field(default=None, description="Task due date and time (optional)")


class TaskResponse(BaseModel):
    """Schema for task information response."""
    id: int = Field(description="Unique task identifier")
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    completed: bool = Field(description="Task completion status")
    created_at: datetime = Field(description="Task creation timestamp")
    updated_at: datetime = Field(description="Task last update timestamp")
    start_at: datetime | None = Field(default=None, description="Task start date and time")
    completed_at: datetime | None = Field(default=None, description="Task completion timestamp (set when task is marked as completed)")
    due_date: datetime | None = Field(default=None, description="Task due date and time")

    model_config = {
        "from_attributes": True
    }


class TaskListResponse(BaseModel):
    """Schema for paginated task list response."""
    tasks: list[TaskResponse] = Field(description="List of tasks")
    pagination: dict | None = Field(default=None, description="Pagination metadata (total, skip, limit, has_more)")

    model_config = {
        "from_attributes": True
    }


# Analytic Schemas
class CountersSchema(BaseModel):
    """Schema for global analytics counters."""
    total_tasks: int = Field(description="Total number of tasks in the system")
    active_tasks: int = Field(description="Number of incomplete tasks")
    completed_tasks: int = Field(description="Number of completed tasks")
    overdue_tasks: int = Field(description="Number of overdue incomplete tasks")
    total_users: int = Field(description="Total number of users in the system")


class TaskLast24HoursSchema(BaseModel):
    """Schema for hourly task statistics within 24 hours."""
    day: datetime = Field(description="Hour timestamp")
    created_tasks: int = Field(description="Number of tasks created during this hour")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this hour")
    completed_tasks: int = Field(description="Number of tasks completed during this hour")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this hour")


class TaskLastDaySchema(BaseModel):
    """Schema for 24-hour aggregated task analytics."""
    data: List[TaskLast24HoursSchema] = Field(description="List of hourly task statistics for the last 24 hours")


class TaskPerDaySchema(BaseModel):
    """Schema for daily task statistics."""
    day: date = Field(description="Date")
    created_tasks: int = Field(description="Number of tasks created on this day")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this day")
    completed_tasks: int = Field(description="Number of tasks completed on this day")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this day")


class TaskLast7DaysSchema(BaseModel):
    """Schema for 7-day aggregated task analytics."""
    data: List[TaskPerDaySchema] = Field(description="List of daily task statistics for the last 7 days")


class TaskPerWeekSchema(BaseModel):
    """Schema for weekly task statistics."""
    day: date = Field(description="Week start date")
    created_tasks: int = Field(description="Number of tasks created during this week")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this week")
    completed_tasks: int = Field(description="Number of tasks completed during this week")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this week")


class TaskLastMonthSchema(BaseModel):
    """Schema for 4-week aggregated task analytics."""
    data: List[TaskPerWeekSchema] = Field(description="List of weekly task statistics for the last 4 weeks")


class UserCountersSchema(BaseModel):
    """Schema for user-specific analytics counters."""
    user_id: int = Field(description="User identifier")
    total_tasks: int = Field(description="Total number of tasks for this user")
    active_tasks: int = Field(description="Number of incomplete tasks for this user")
    completed_tasks: int = Field(description="Number of completed tasks for this user")
    overdue_tasks: int = Field(description="Number of overdue incomplete tasks for this user")
    overdue_percent: float = Field(description="Percentage of overdue tasks (0-100)")


class UserTaskLast24HoursSchema(BaseModel):
    """Schema for user-specific hourly task statistics within 24 hours."""
    user_id: int = Field(description="User identifier")
    day: datetime = Field(description="Hour timestamp")
    created_tasks: int = Field(description="Number of tasks created by this user during this hour")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this hour")
    completed_tasks: int = Field(description="Number of tasks completed by this user during this hour")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this hour")
    overdue_percent: float = Field(description="Percentage of overdue tasks at the end of this hour (0-100)")


class UserTaskLastDaySchema(BaseModel):
    """Schema for user-specific 24-hour aggregated task analytics."""
    data: List[UserTaskLast24HoursSchema] = Field(description="List of hourly task statistics for the last 24 hours")


class UserTaskPerDaySchema(BaseModel):
    """Schema for user-specific daily task statistics."""
    user_id: int = Field(description="User identifier")
    day: date = Field(description="Date")
    created_tasks: int = Field(description="Number of tasks created by this user on this day")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this day")
    completed_tasks: int = Field(description="Number of tasks completed by this user on this day")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this day")
    overdue_percent: float = Field(description="Percentage of overdue tasks at the end of this day (0-100)")


class UserTaskLast7DaysSchema(BaseModel):
    """Schema for user-specific 7-day aggregated task analytics."""
    data: List[UserTaskPerDaySchema] = Field(description="List of daily task statistics for the last 7 days")


class UserTaskPerWeekSchema(BaseModel):
    """Schema for user-specific weekly task statistics."""
    user_id: int = Field(description="User identifier")
    day: date = Field(description="Week start date")
    created_tasks: int = Field(description="Number of tasks created by this user during this week")
    active_tasks: int = Field(description="Number of active (incomplete) tasks at the end of this week")
    completed_tasks: int = Field(description="Number of tasks completed by this user during this week")
    overdue_tasks: int = Field(description="Number of overdue tasks at the end of this week")
    overdue_percent: float = Field(description="Percentage of overdue tasks at the end of this week (0-100)")


class UserTaskLastMonthSchema(BaseModel):
    """Schema for user-specific 4-week aggregated task analytics."""
    data: List[UserTaskPerWeekSchema] = Field(description="List of weekly task statistics for the last 4 weeks")