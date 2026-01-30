from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from apps.schemas import (
    CountersSchema,
    TaskLast7DaysSchema,
    TaskLast24HoursSchema,
    TaskLastDaySchema,
    TaskLastMonthSchema,
    TaskPerDaySchema,
    TaskPerWeekSchema,
    UserCountersSchema,
    UserTaskLast7DaysSchema,
    UserTaskLast24HoursSchema,
    UserTaskLastDaySchema,
    UserTaskLastMonthSchema,
    UserTaskPerDaySchema,
    UserTaskPerWeekSchema,
)
from database.models import User

from .cache import AnalyticsCache
from .repository import AnalyticsRepository, UserAnalyticsRepository


class AnalyticsPeriod(str, Enum):
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_4_WEEKS = "4w"


class AnalyticsService:
    GLOBAL_COUNTERS_KEY = "analytics:global"
    TASKS_24H_KEY = "analytics:global_aggregated:24h"
    TASKS_7D_KEY = "analytics:global_aggregated:7d"
    TASKS_4W_KEY = "analytics:global_aggregated:4w"

    GLOBAL_TTL = 3600
    GLOBAL_HOUR_TTL = 1800

    _PERIOD_HANDLERS = {
        AnalyticsPeriod.LAST_24_HOURS: "get_tasks_last_24_hours",
        AnalyticsPeriod.LAST_7_DAYS: "get_tasks_last_7_days",
        AnalyticsPeriod.LAST_4_WEEKS: "get_tasks_last_4_weeks",
    }

    def __init__(self, db: AsyncSession, cache: AnalyticsCache):
        self.db = db
        self.cache = cache

    async def get_global_counters(self) -> CountersSchema:
        cached = await self.cache.get(self.GLOBAL_COUNTERS_KEY)
        if cached is not None:
            return CountersSchema(**cached)

        data = await AnalyticsRepository.get_global_counters(self.db)
        await self.cache.set(self.GLOBAL_COUNTERS_KEY, data, self.GLOBAL_TTL)

        return CountersSchema(**data)

    async def get_by_period(self, period: AnalyticsPeriod):
        method_name = self._PERIOD_HANDLERS.get(period)

        if not method_name:
            raise ValueError(f"Unsupported analytics period: {period}")

        handler = getattr(self, method_name)
        return await handler()

    async def get_tasks_last_24_hours(self) -> TaskLastDaySchema:
        cached = await self.cache.get(self.TASKS_24H_KEY)
        if cached is not None:
            return TaskLastDaySchema(
                data=[TaskLast24HoursSchema(**row) for row in cached]
            )

        rows = await AnalyticsRepository.get_tasks_last_24_hours(self.db)
        await self.cache.set(self.TASKS_24H_KEY, rows, self.GLOBAL_HOUR_TTL)

        return TaskLastDaySchema(
            data=[TaskLast24HoursSchema(**row) for row in rows]
        )

    async def get_tasks_last_7_days(self) -> TaskLast7DaysSchema:
        cached = await self.cache.get(self.TASKS_7D_KEY)
        if cached is not None:
            return TaskLast7DaysSchema(
                data=[TaskPerDaySchema(**row) for row in cached]
            )

        rows = await AnalyticsRepository.get_tasks_last_7_days(self.db)
        await self.cache.set(self.TASKS_7D_KEY, rows, self.GLOBAL_TTL)

        return TaskLast7DaysSchema(
            data=[TaskPerDaySchema(**row) for row in rows]
        )

    async def get_tasks_last_4_weeks(self) -> TaskLastMonthSchema:
        cached = await self.cache.get(self.TASKS_4W_KEY)
        if cached is not None:
            return TaskLastMonthSchema(
                data=[TaskPerWeekSchema(**row) for row in cached]
            )

        rows = await AnalyticsRepository.get_tasks_last_4_weeks(self.db)
        await self.cache.set(self.TASKS_4W_KEY, rows, self.GLOBAL_TTL)

        return TaskLastMonthSchema(
            data=[TaskPerWeekSchema(**row) for row in rows]
        )


class UserAnalyticsService:
    USER_GLOBAL_KEY = "analytics:user:{user_id}"
    TASKS_24H_KEY = "analytics:user:{user_id}:24h"
    TASKS_7D_KEY = "analytics:user:{user_id}:7d"
    TASKS_4W_KEY = "analytics:user:{user_id}:4w"

    USER_TTL = 3600
    USER_HOUR_TTL = 300

    _PERIOD_HANDLERS = {
        AnalyticsPeriod.LAST_24_HOURS: "get_user_tasks_last_24_hours",
        AnalyticsPeriod.LAST_7_DAYS: "get_user_tasks_last_7_days",
        AnalyticsPeriod.LAST_4_WEEKS: "get_user_tasks_last_4_weeks",
    }

    def __init__(self, db: AsyncSession, cache: AnalyticsCache, user: User):
        self.db = db
        self.cache = cache
        self.user = user

    async def get_user_analytics(self) -> UserCountersSchema:
        key = self.USER_GLOBAL_KEY.format(user_id=self.user.id)

        cached = await self.cache.get(key)
        if cached is not None:
            return UserCountersSchema(**cached)

        data = await UserAnalyticsRepository.get_user_analytics(self.db, self.user.id)
        await self.cache.set(key, data, self.USER_TTL)

        return UserCountersSchema(**data)

    async def get_user_analytics_by_period(self, period: AnalyticsPeriod):
        method_name = self._PERIOD_HANDLERS.get(period)

        if not method_name:
            raise ValueError(f"Unsupported analytics period: {period}")

        handler = getattr(self, method_name)
        return await handler()

    async def get_user_tasks_last_24_hours(self) -> UserTaskLastDaySchema:
        key = self.TASKS_24H_KEY.format(user_id=self.user.id)

        cached = await self.cache.get(key)
        if cached is not None:
            return UserTaskLastDaySchema(
                data=[UserTaskLast24HoursSchema(**row) for row in cached]
            )

        rows = await UserAnalyticsRepository.get_user_tasks_last_24_hours(self.db, self.user.id)
        await self.cache.set(key, rows, self.USER_HOUR_TTL)

        return UserTaskLastDaySchema(
            data=[UserTaskLast24HoursSchema(**row) for row in rows]
        )

    async def get_user_tasks_last_7_days(self) -> UserTaskLast7DaysSchema:
        key = self.TASKS_7D_KEY.format(user_id=self.user.id)

        cached = await self.cache.get(key)
        if cached is not None:
            return UserTaskLast7DaysSchema(
                data=[UserTaskPerDaySchema(**row) for row in cached]
            )

        rows = await UserAnalyticsRepository.get_user_tasks_last_7_days(self.db, self.user.id)
        await self.cache.set(key, rows, self.USER_TTL)

        return UserTaskLast7DaysSchema(
            data=[UserTaskPerDaySchema(**row) for row in rows]
        )

    async def get_user_tasks_last_4_weeks(self) -> UserTaskLastMonthSchema:
        key = self.TASKS_4W_KEY.format(user_id=self.user.id)

        cached = await self.cache.get(key)
        if cached is not None:
            return UserTaskLastMonthSchema(
                data=[UserTaskPerWeekSchema(**row) for row in cached]
            )

        rows = await UserAnalyticsRepository.get_user_tasks_last_4_weeks(self.db, self.user.id)
        await self.cache.set(key, rows, self.USER_TTL)

        return UserTaskLastMonthSchema(
            data=[UserTaskPerWeekSchema(**row) for row in rows]
        )
