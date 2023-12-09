from context import ctx
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from deps import get_current_user
from shared.entities import User

import logging

stats_router = APIRouter()

logger = logging.getLogger("app")


@stats_router.get("/stats")
async def get_stats(
    user: Annotated[User, Depends(get_current_user)],
    start_date: str | None = None,
    end_date: str | None = None,
):
    if start_date is None or end_date is None:
        return await ctx.stats_repo.get_many(field="user_id", value=user.id)

    return await ctx.stats_repo.get_many_in_timestamp("start_timestamp", start_date, end_date, {"user_id": user.id})
