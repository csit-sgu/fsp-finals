from context import ctx
from fastapi import APIRouter
from models import Block

from shared.routes import TaskRoutes

block_router = APIRouter()


@block_router.get(TaskRoutes.BLOCK)
@block_router.get("/tasks")
async def get_tasks():
    return await ctx.task_repo.get_many()


@block_router.get(TaskRoutes.BLOCK + "{id}")
async def get_task(id: str):
    return await ctx.block_repo.get_many(field="task_id", value=id)


@block_router.post(TaskRoutes.BLOCK + "/{id}")
async def add_task(block: Block):
    return await ctx.block_repo.add()

@block_router.patch(TaskRoutes.BLOCK + "/{task_id}")
async def partial_update(task_id: int, block: Block)
    # TODO(nrydanov): Добавить кэширование в Redis
    pass
