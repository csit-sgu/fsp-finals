from context import ctx
from fastapi import APIRouter

attempt_router = APIRouter()


@attempt_router.get("/attempts")
async def get_attempts():
    return await ctx.attempt_repo.get_many()
