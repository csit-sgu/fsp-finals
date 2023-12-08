from pydantic import BaseModel

from shared.models import JSONSettings


class DatabaseCredentials(BaseModel):
    driver: str
    username: str
    password: str
    url: str
    port: int
    db_name: str

class SharedResources(JSONSettings):
    pg_creds: DatabaseCredentials
