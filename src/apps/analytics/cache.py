import json
from typing import Any, Optional


class AnalyticsCache:
    """Cache wrapper for analytics data using Redis."""

    def __init__(self, redis):
        """Initialize cache with Redis client."""
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value by key."""
        raw = await self.redis.get(key)
        if not raw:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int):
        """Set cached value with TTL."""
        await self.redis.set(
            key,
            json.dumps(value, default=str),
            ex=ttl
        )


class AnalyticsCacheInvalidator:
    """Cache invalidator for analytics data."""

    def __init__(self, redis):
        """Initialize cache invalidator with Redis client."""
        self.redis = redis
        self.count: int = 500

    async def delete_by_key(self, key: str) -> None:
        """Delete cache entry by key."""
        await self.redis.delete(key)

    async def delete_by_patterns(self, patterns: list[str]) -> None:
        """Delete cache entries matching patterns."""
        for pattern in patterns:
            keys_to_delete = []

            async for key in self.redis.scan_iter(match=pattern, count=self.count):
                keys_to_delete.append(key)

                if len(keys_to_delete) >= self.count:
                    await self.redis.unlink(*keys_to_delete)
                    keys_to_delete = []

            if keys_to_delete:
                await self.redis.unlink(*keys_to_delete)

    async def invalidate_user(self, user_id: int) -> None:
        """Invalidate all cache entries for a specific user."""
        keys = [
            f"analytics:user:{user_id}",
            f"analytics:user:{user_id}:*",
        ]
        await self.delete_by_patterns(keys)
