import json

from pydantic import BaseModel
from datetime import date


class JSONSettings(BaseModel):
    def __init__(self, path: str):
        with open(path, "r") as f:
            config_data = json.load(f)
            return super().__init__(**config_data)

    class Config:
        populate_by_name = True


class User(BaseModel):
    username: str
    password: bytes
    is_admin: bool
    birthdate: date
    name: str
    surname: str
    weekly_score: float


class Task(BaseModel):
    category: str
    entry_id: int
