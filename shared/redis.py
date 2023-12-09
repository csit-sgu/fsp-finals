import datetime
import logging

from uuid import UUID
from typing import Dict
import redis.asyncio as redis

logger = logging.getLogger("app")


class RedisRepository:
    def __init__(self, redis: redis.Redis, type: str):
        self._redis: redis.Redis = redis
        self._document_name: str = type

    async def cleanup(self):
        now = datetime.now()
        keys = self._redis.execute_command(f"keys *{self._document_name}*")
        for key in keys:
            data = self._redis.hgetall(key)
            for timestamp, value in data.items():
                if now - timestamp > datetime.timedelta(seconds=5):
                    self._redis.hdel(key, value)


class ContainerRepository(RedisRepository):
    async def get(self, user_id: UUID, block_id: UUID):
        return await self._redis.hgetall(
            f"{self._document_name}:{user_id}:{block_id}"
        )

    async def add_or_update(self, user_id: UUID, block_id: UUID, payload: Dict):
        await self._redis.hset(
            f"{self._document_name}:{user_id}:{block_id}", mapping=payload
        )
