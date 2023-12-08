from context import ctx
from fastapi import APIRouter

block_router = APIRouter()


@block_router.get("/block/{id}")
async def get_block(id: str):
    return await ctx.block_repo.get_one(field="block_id", value=id)
