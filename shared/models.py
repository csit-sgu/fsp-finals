import json
from typing import Dict, List

from enum import Enum
from pydantic import BaseModel
from datetime import date
from uuid import UUID
from datetime import datetime

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
    CONTAINER = "container"


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
    is_for_subs: bool
    category: str
    entry_id: UUID


class QuizFrontend(BaseModel):
    title: str
    author_username: str
    description: str
    category: models.Category
    complexity: int
    age_group: models.AgeGroup
    is_for_subs: bool
    blocks: List[BlockFrontend]


class ContainerRequest(BaseModel):
    
    class Payload(BaseModel):
        image_name: str
        image_tag: str | None = None
        ttl: int
        expected_output: str

    payload: Payload


class ValidateRequest(BaseModel):
    answer: str

class User(BaseModel):
    username: str
    password: bytes
    is_admin: bool = False
    passed_test: bool
    is_subscriber: bool
    birth_date: date
    name: str
    surname: str
    weekly_goal: float


class Answer(BaseModel):
    block_id: UUID
    answer: str | List[str]


class AttemptFrontend(BaseModel):
    quiz_id: UUID
    quiz_title: str
    username: str
    answers: List[Answer]


class AttemptFeedback(BaseModel):
    block_id: UUID
    correctness: int
    score: float
    feedback: str = ""


class Attempt(BaseModel):
    quiz_id: UUID
    quiz_title: str
    user_id: UUID
    quiz_score: float
    time_passed: int
    start_timestamp: datetime
