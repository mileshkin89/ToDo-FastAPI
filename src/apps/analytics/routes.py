from fastapi import APIRouter, Depends, Query

from .dependencies import get_analytics_service, get_user_analytics_service
from .service import AnalyticsPeriod, AnalyticsService, UserAnalyticsService

analytics_router = APIRouter()


@analytics_router.get("/global")
async def global_analytics(
        service: AnalyticsService = Depends(get_analytics_service),
):
    return {
        "counters": await service.get_global_counters()
    }


@analytics_router.get("/global_aggregated")
async def global_analytics_aggregated(
        period: AnalyticsPeriod = Query("7d", description="Aggregation period"),
        service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_by_period(period)


@analytics_router.get("/users_global")
async def user_analytics(
        service: UserAnalyticsService = Depends(get_user_analytics_service),
):
    return {
        "counters": await service.get_user_analytics()
    }


@analytics_router.get("/users_aggregated")
async def user_analytics_aggregated(
        period: AnalyticsPeriod = Query("7d", description="Aggregation period"),
        service: UserAnalyticsService = Depends(get_user_analytics_service),
):
    return await service.get_user_analytics_by_period(period)
