import datetime
import logging

from uuid import UUID
from typing import Dict
import redis

logger = logging.getLogger("app")


class RedisRepository:
    def __init__(self, redis: redis.Redis, type: str):
        self._redis: redis.Redis = redis
        self._table_name: str = type

    async def add_or_update_quiz(self, user_id: UUID, payload: Dict):
        self._redis.hset(f"{self._table_name}:{user_id}", mapping=payload)

    async def add_or_update_attempt(
        self, user_id: UUID, task_id: UUID, score: float
    ):
        self._redis.hset(f"{self._table_name}:{user_id}", task_id, score)

    async def get_quiz(self, user_id: UUID):
        return self._redis.hgetall(f"{self._table_name}:{user_id}")

    async def cleanup(self):
        now = datetime.now()
        keys = self._redis.execute_command(f"keys *{self._table_name}*")
        for key in keys:
            data = self._redis.hgetall(key)
            for timestamp, value in data.items():
                if now - timestamp > datetime.timedelta(seconds=5):
                    self._redis.hdel(key, value)
