import redis.asyncio as redis

class RedisClient:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def set(self, key: str, value: str, ex=None):
        await self.redis.set(key, value, ex=ex)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def exists(self, key: str):
        return await self.redis.exists(key)
