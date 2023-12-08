from typing import ClassVar

from shared.db import Entity


class User(Entity):
    email: str
    password: bytes

    _table_name: ClassVar[str] = "users"
    _pk: ClassVar[str] = "id"
