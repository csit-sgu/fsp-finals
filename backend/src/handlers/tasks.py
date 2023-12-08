from uuid import UUID

from context import ctx
from fastapi import APIRouter
from typing import Dict

task_router = APIRouter()


@task_router.get("/tasks")
async def get_quizzes(
    age_category: str | None = None,
    quiz_category: str | None = None,
    complexity: str | None = None,
):
    filters = dict()
    if age_category is not None:
        filters["age_category"] = age_category

    if quiz_category is not None:
        filters["category"] = quiz_category

    if complexity is not None:
        filters["complexity"] = complexity
    return await ctx.quiz_repo.get_many_filtered(filters)


@task_router.get("/task/{id}")
async def get_task(id: UUID):
    return await ctx.quiz_repo.get_one(field="task_id", value=id)


@task_router.post("/task/{task_id}")
async def add_task(task_id):
    pass
