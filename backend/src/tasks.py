from context import ctx
from shared.models import Task
from main import app


@app.get("/tasks")
async def get_tasks():
    return await ctx.task_repo.get_many()


@app.get("/tasks/{id}")
async def get_task(id: int):
    return await ctx.task_repo.get_one(field="task_id", value=id)


@app.post("/tasks")
async def add_task(task: Task):
    return await ctx.task_repo.add(task)
