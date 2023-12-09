import logging
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi.middleware.cors import CORSMiddleware

import asyncpg
from asgi_correlation_id import CorrelationIdMiddleware
from context import ctx
from deps import get_current_user
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from handlers.attempts import attempt_router
from handlers.blocks import block_router
from handlers.quiz import quiz_router
from handlers.stats import stats_router
from jose import JWTError, jwt
from pydantic import ValidationError
from utils import (
    TokenPayload,
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

from shared.logger import configure_logging
from shared.entities import User
from shared.routes import UserRoutes
import shared.models as models


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await ctx.init_db()
    await ctx.user_repo.add(
        models.User(
            username="aboba",
            password=hash_password(b"aboba"),
            is_admin=True,
            birth_date="2003-01-18",
            name="Michael",
            surname="Chernigin",
            weekly_goal=100,
        ),
        ignore_conflict=True,
    )
    yield
    await ctx.dispose_db()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
logger = logging.getLogger("app")

app.include_router(quiz_router)
app.include_router(attempt_router)
app.include_router(block_router)
app.include_router(stats_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Say hi.")
async def hi() -> str:
    return "hi."


@app.post(
    UserRoutes.REGISTER,
    summary="Register new user",
    status_code=status.HTTP_201_CREATED,
)
async def register(user: User):
    try:
        user.password = hash_password(user.password)
        await ctx.user_repo.add(user)
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=400, detail="User with this username already exists"
        )


@app.post(
    UserRoutes.AUTH,
    summary="Create access and refresh tokens for user",
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
):
    err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    found_entity = await ctx.user_repo.get_one(
        field="username", value=form_data.username
    )
    if found_entity is None:
        raise err
    user = User.model_validate(found_entity)
    if not verify_password(
        password=str.encode(form_data.password), known_hash=user.password
    ):
        raise err

    access_token = create_access_token(ctx, data={"sub": user.username})
    refresh_token = create_refresh_token(ctx, data={"sub": user.username})

    response.set_cookie(key="Access-Token", value=access_token, httponly=True)
    response.set_cookie(
        key="Refresh-Token",
        value=refresh_token,
        httponly=True,
        path="/refresh",
    )


@app.post(
    UserRoutes.REFRESH, summary="Refresh access token using refresh token"
)
async def refresh(request: Request, response: Response):
    err = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        refresh_token = request.cookies.get("Refresh-Token")
        if refresh_token is None:
            raise err
        payload = jwt.decode(
            token=refresh_token,
            key=ctx.jwt_secret_key,
            algorithms=[ctx.hash_algorithm],
        )
        payload = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise err

    access_token = create_access_token(
        ctx,
        data={"sub": payload.sub},
        expires_delta=timedelta(minutes=ctx.access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(ctx, data={"sub": payload.sub})
    response.set_cookie(key="Access-Token", value=access_token, httponly=True)
    response.set_cookie(
        key="Refresh-Token",
        value=refresh_token,
        httponly=True,
        path="/refresh",
    )


@app.get(UserRoutes.LOGOUT, summary="Logout of user account")
async def logout(response: Response):
    response.delete_cookie(key="Access-Token")


@app.get(UserRoutes.ME, summary="Get secret that only register people know")
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


# TODO: delete me
@app.get(UserRoutes.REGISTER, status_code=status.HTTP_200_OK)
async def get_users():
    return await ctx.user_repo.get_many()
