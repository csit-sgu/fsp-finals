from typing import ClassVar
from typing import Dict

from shared.db import Entity

from uuid import uuid
from datetime import date, datetime


class User(Entity):
    id: uuid
    username: str
    password: bytes
    is_admin: bool
    birthdate: date
    name: str
    surname: str
    weekly_score: float

    _table_name: ClassVar[str] = "users"
    _pk: ClassVar[str] = "id"


class Task(Entity):
    task_id: int
    category: str
    entry_id: int

    _table_name: ClassVar[str] = "tasks"
    _pk = "task_id"


class Block(Entity):
    block_id: int
    author_id: uuid
    block_type: str
    payload: Dict  # json?

    _table_name: ClassVar[str] = "blocks"
    _pk = "block_id"


class Attempt(Entity):
    attempt_id: int
    task_id: int
    user_id: uuid
    task_score: float
    time_passed: int
    start_timestamp: datetime

    _table_name: ClassVar[str] = "attempts"
    _pk = "attempt_id"


class TaskComplexity(Entity):
    task_id: uuid
    age_category: str
    complexity: str

    _table_name: ClassVar[str] = "task_complexity"


class RunningContainer(Entity):
    container_id: str
    user_id: uuid
    block_id: int
    start_timestamp: datetime
    host_ip: str
    host_port: str

    _table_name: ClassVar[str] = "running_containers"
