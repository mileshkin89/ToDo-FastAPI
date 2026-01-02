from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from settings import settings

redis_pool: ConnectionPool | None = None


def init_redis() -> None:
    global redis_pool

    redis_pool = ConnectionPool.from_url(
        settings.redis_url,
        max_connections=10,
        decode_responses=True,
    )


async def get_redis() -> Redis:
    if redis_pool is None:
        raise RuntimeError("Redis pool is not initialized")

    redis = Redis(connection_pool=redis_pool)
    try:
        yield redis
    finally:
        await redis.close()
