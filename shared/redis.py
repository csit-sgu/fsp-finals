import datetime
import logging

import redis

from shared.models import MetricType

logger = logging.getLogger("app")


class RedisRepository:
    def __init__(self, redis: redis.Redis, metric: MetricType):
        self._redis: redis.Redis = redis
        self._table_name: str = metric.value

    async def add(self, source_id: str, score: int):
        logger.debug(f"Redis.add {source_id=} {score=}")
        self._redis.hset(f"{self._table_name}:{source_id}", score)

    async def get(self, source_id: str):
        logger.debug(f"Redis.get {source_id=}")
        return self._redis.hgetall(f"{self._table_name}:{source_id}")

    async def cleanup(self):
        logger.debug("Redis.cleanup")
        now = datetime.now()
        keys = self._redis.execute_command(f"keys *{self._table_name}*")
        for key in keys:
            data = self._redis.hgetall(key)
            for timestamp, value in data.items():
                if now - timestamp > datetime.timedelta(seconds=5):
                    logger.debug(f"delete {key} {self._table_name} {value}")
                    self._redis.hdel(key, value)
