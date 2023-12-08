from pyauth.context import ctx
from pyauth.models import Task
from pyauth.main import app


@app.get("/tasks")
async def get_tasks():
    return ctx.task_repo.get_many()


@app.get("/tasks/{id}")
async def get_task(id: int):
    return ctx.task_repo.get_one(field="task_id", value=id)


@app.post("/tasks")
async def add_task(task: Task):
    return ctx.task_repo.add(task)
