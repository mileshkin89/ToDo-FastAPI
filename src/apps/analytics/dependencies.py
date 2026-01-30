from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from apps.analytics.cache import AnalyticsCache, AnalyticsCacheInvalidator
from apps.analytics.service import AnalyticsService, UserAnalyticsService
from apps.auth.dependencies import get_current_user
from database.db import get_db
from database.models import User
from infrastructure.redis.client import get_redis


async def get_analytics_service(
        db: AsyncSession = Depends(get_db),
        redis: Redis = Depends(get_redis),
) -> AnalyticsService:
    cache = AnalyticsCache(redis)

    return AnalyticsService(
        db=db,
        cache=cache,
    )


async def get_user_analytics_service(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        redis=Depends(get_redis),
) -> UserAnalyticsService:
    cache = AnalyticsCache(redis)

    return UserAnalyticsService(
        db=db,
        cache=cache,
        user=current_user
    )


async def get_cache_invalidator(
        redis=Depends(get_redis),

) -> AnalyticsCacheInvalidator:
    return AnalyticsCacheInvalidator(redis)