from typing import AsyncIterator

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from settings import settings

_redis_pool: ConnectionPool | None = None


async def get_pool() -> ConnectionPool:
    global _redis_pool

    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=10,
            decode_responses=True,
        )
    return _redis_pool


async def cleanup_pool() -> None:
    global _redis_pool

    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


async def get_redis() -> AsyncIterator[Redis]:
    await get_pool()

    if _redis_pool is None:
        raise RuntimeError("Redis pool not initialized")

    redis = Redis(connection_pool=_redis_pool)
    try:
        yield redis
    finally:
        await redis.close()
