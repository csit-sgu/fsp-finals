from datetime import date, datetime
from typing import ClassVar
from uuid import UUID

from shared.db import Entity


class User(Entity):
    id: UUID
    username: str
    password: bytes
    is_admin: bool
    passed_test: bool
    birth_date: date
    name: str
    surname: str
    weekly_goal: float

    _table_name: ClassVar[str] = "users"
    _pk: ClassVar[str] = "id"


class Quiz(Entity):
    quiz_id: UUID
    title: str
    author_id: UUID
    description: str
    is_for_subs: bool
    category: str
    entry_id: UUID

    _table_name: ClassVar[str] = "quizzes"
    _pk = "quiz_id"


class QuizInfo(Entity):
    quiz_id: UUID
    title: str
    author_id: UUID
    description: str
    category: str
    entry_id: UUID
    age_group: str
    complexity: int

    _table_name: ClassVar[str] = "quiz_info"


class Block(Entity):
    block_id: UUID
    block_type: str
    problem: str
    payload: str  # json?

    _table_name: ClassVar[str] = "blocks"
    _pk = "block_id"


class Attempt(Entity):
    attempt_id: int
    quiz_id: UUID
    user_id: UUID
    quiz_score: float
    time_passed: int
    start_timestamp: datetime

    _table_name: ClassVar[str] = "attempts"
    _pk = "attempt_id"


class QuizComplexity(Entity):
    quiz_id: UUID
    age_group: str
    complexity: int

    _table_name: ClassVar[str] = "quiz_complexities"


class AttemptStat(Entity):
    quiz_id: UUID
    start_timestamp: datetime
    score: float

    _table_name: ClassVar[str] = "stats"
