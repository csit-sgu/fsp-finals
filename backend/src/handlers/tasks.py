from uuid import UUID

from context import ctx
from fastapi import APIRouter

task_router = APIRouter()


@task_router.get("/tasks")
async def get_tasks():
    return await ctx.quiz_repo.get_many()


@task_router.get("/task/{id}")
async def get_task(id: UUID):
    return await ctx.quiz_repo.get_one(field="task_id", value=id)


@task_router.post("/task/{task_id}")
async def add_task(task_id):
    pass
