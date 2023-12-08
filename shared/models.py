import json
from typing import Dict, List

from enum import Enum, IntEnum
from pydantic import BaseModel
from datetime import date
from uuid import UUID

import shared.models as models


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config_data = json.load(f)
            return super().__init__(**config_data)

    class Config:
        populate_by_name = True


class AgeGroup(str, Enum):
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"


age_group_ranges = {
    AgeGroup.CHILD: (0, 12),
    AgeGroup.TEEN: (12, 16),
    AgeGroup.ADULT: (16, 150),
}


class Category(str, Enum):
    FINANCE = "finance"
    PERSONAL_DATA = "personal_data"
    DEVICES_SECURITY = "devices_security"
    WEB = "web"


class BlockType(str, Enum):
    FREE_ANSWER = "free_answer"
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    CASE = "case"


class BlockFrontend(BaseModel):
    block_id: int
    problem: str
    block_type: BlockType
    payload: Dict  # JSON


class Block(BaseModel):
    block_id: UUID  # UUID
    problem: str
    block_type: BlockType
    payload: str  # JSON


class Quiz(BaseModel):
    title: str
    author_id: UUID
    description: str
    category: str
    entry_id: UUID


class QuizFrontend(BaseModel):
    title: str
    author_username: str
    description: str
    category: models.Category
    complexity: int
    age_group: models.AgeGroup
    blocks: List[BlockFrontend]


class User(BaseModel):
    username: str
    password: bytes
    is_admin: bool = False
    birth_date: date
    name: str
    surname: str
    weekly_goal: float


class Answer(BaseModel):
    block_id: UUID
    answer: str | List[str]


class AttemptFrontend(BaseModel):
    quiz_id: UUID
    username: str
    answers: List[Answer]
