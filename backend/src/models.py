from enum import Enum

from pydantic import BaseModel


class BlockType(str, Enum):
    FREE_ANSWER = "free_answer"
    MULTIPLE_CHOICE = "multiple_choice"
    CASE = "case"


class Block(BaseModel):
    block_id: str  # UUID
    block_type: BlockType
    problem: str
    payload: str  # JSON
