import json
from typing import List, Dict

from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from datetime import date
from uuid import UUID


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config_data = json.load(f)
            return super().__init__(**config_data)

    class Config:
        populate_by_name = True


class BlockType(str, Enum):
    FREE_ANSWER = "free_answer"
    MULTIPLE_CHOICE = "multiple_choice"
    CASE = "case"


class BlockFrontend(BaseModel):
    block_id: int
    block_type: BlockType
    payload: str  # JSON


class Block(BaseModel):
    block_id: UUID  # UUID
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
    category: str
    blocks: List[Block]


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
    answer: str


class Attempt(BaseModel):
    quiz_id: int
    username: str
    answers: List[Answer]
