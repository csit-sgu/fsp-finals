from datetime import datetime

from context import ctx
from entities import User
from fastapi import HTTPException, status
from jose import JWTError, jwt
from pydantic import ValidationError
from starlette.requests import Request

from utils import TokenPayload


async def get_current_user(request: Request) -> User:
    try:
        access_token = request.cookies.get("Access-Token")
        if access_token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = jwt.decode(
            token=access_token,
            key=ctx.jwt_secret_key,
            algorithms=[ctx.hash_algorithm],
        )
        token_data = TokenPayload(**payload)
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    found_entity = await ctx.user_repo.get_one(field="username", value=token_data.sub)
    if found_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return User.model_validate(found_entity)
