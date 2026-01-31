from fastapi import APIRouter, Depends, Query

from .dependencies import get_analytics_service, get_user_analytics_service
from .service import AnalyticsPeriod, AnalyticsService, UserAnalyticsService

analytics_router = APIRouter()


@analytics_router.get(
    "/global",
    summary="Get global analytics counters",
    description="Retrieve global analytics counters including total tasks, active tasks, completed tasks, overdue tasks, and total users. Results are cached for performance.",
    response_description="Global analytics counters"
)
async def global_analytics(
        service: AnalyticsService = Depends(get_analytics_service),
):
    return {
        "counters": await service.get_global_counters()
    }


@analytics_router.get(
    "/global_aggregated",
    summary="Get global aggregated analytics",
    description="Retrieve time-aggregated global analytics data for tasks. Supports periods: 24h (last 24 hours), 7d (last 7 days), or 4w (last 4 weeks). Results are cached for performance.",
    response_description="Time-aggregated global analytics data"
)
async def global_analytics_aggregated(
        period: AnalyticsPeriod = Query("7d", description="Aggregation period"),
        service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_by_period(period)


@analytics_router.get(
    "/users_global",
    summary="Get user analytics counters",
    description="Retrieve analytics counters for the authenticated user including total tasks, active tasks, completed tasks, overdue tasks, and overdue percentage. Results are cached for performance.",
    response_description="User analytics counters"
)
async def user_analytics(
        service: UserAnalyticsService = Depends(get_user_analytics_service),
):
    return {
        "counters": await service.get_user_analytics()
    }


@analytics_router.get(
    "/users_aggregated",
    summary="Get user aggregated analytics",
    description="Retrieve time-aggregated analytics data for the authenticated user's tasks. Supports periods: 24h (last 24 hours), 7d (last 7 days), or 4w (last 4 weeks). Results are cached for performance.",
    response_description="Time-aggregated user analytics data"
)
async def user_analytics_aggregated(
        period: AnalyticsPeriod = Query("7d", description="Aggregation period"),
        service: UserAnalyticsService = Depends(get_user_analytics_service),
):
    return await service.get_user_analytics_by_period(period)
