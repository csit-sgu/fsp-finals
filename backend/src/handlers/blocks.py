from context import ctx
from fastapi import APIRouter, HTTPException

block_router = APIRouter()


@block_router.get("/block/{id}")
async def get_block(id: str):
    block = await ctx.block_repo.get_one(field="block_id", value=id)

    if block is None:
        raise HTTPException(status_code=404, detail="Block not found")

    return block