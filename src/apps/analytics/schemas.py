from datetime import date, datetime
from typing import List

from pydantic import BaseModel


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
