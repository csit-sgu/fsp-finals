from datetime import date, datetime
from typing import ClassVar, Dict
from uuid import UUID

from shared.db import Entity


class User(Entity):
    id: UUID
    username: str
    password: bytes
    is_admin: bool
    birthdate: date
    name: str
    surname: str
    weekly_score: float

    _table_name: ClassVar[str] = "users"
    _pk: ClassVar[str] = "id"


class Quiz(Entity):
    quiz_id: int
    title: str
    description: str
    category: str
    entry_id: UUID

    _table_name: ClassVar[str] = "quizzes"
    _pk = "quiz_id"


class Block(Entity):
    block_id: UUID
    author_id: UUID
    block_type: str
    payload: Dict  # json?

    _table_name: ClassVar[str] = "blocks"
    _pk = "block_id"


class Attempt(Entity):
    attempt_id: int
    quiz_id: int
    user_id: UUID
    quiz_score: float
    time_passed: int
    start_timestamp: datetime

    _table_name: ClassVar[str] = "attempts"
    _pk = "attempt_id"


class QuizComplexity(Entity):
    quiz_id: UUID
    age_category: str
    complexity: str

    _table_name: ClassVar[str] = "quiz_complexities"


class RunningContainer(Entity):
    container_id: str
    user_id: UUID
    block_id: UUID
    start_timestamp: datetime
    host_ip: str
    host_port: str

    _table_name: ClassVar[str] = "running_containers"