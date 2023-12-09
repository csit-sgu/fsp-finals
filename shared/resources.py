from pydantic import BaseModel

from shared.models import JSONSettings
from typing import List


class DatabaseCredentials(BaseModel):
    driver: str
    username: str
    password: str
    url: str
    port: int
    db_name: str


class DockerHost(BaseModel):
    base_url: str
    version: str


class DockerSettings(BaseModel):
    docker_hosts: List[DockerHost]
    max_pool_size: int
    default_image: str


class RedisCredentials(BaseModel):
    username: str
    password: str
    host: str
    port: int


class SharedResources(JSONSettings):
    pg_creds: DatabaseCredentials
    redis_creds: RedisCredentials
    openai_key: str
    docker_settings: DockerSettings
    default_container_ttl: int = 30
