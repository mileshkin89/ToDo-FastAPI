import json
from typing import Any, Optional


class AnalyticsCache:

    def __init__(self, redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[Any]:
        raw = await self.redis.get(key)
        if not raw:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl: int):
        await self.redis.set(
            key,
            json.dumps(value, default=str),
            ex=ttl
        )


class AnalyticsCacheInvalidator:

    def __init__(self, redis):
        self.redis = redis
        self.count: int = 500

    async def delete_by_key(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_by_patterns(self, patterns: list[str]) -> None:
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
        keys = [
            f"analytics:user:{user_id}",
            f"analytics:user:{user_id}:*",
        ]
        await self.delete_by_patterns(keys)
