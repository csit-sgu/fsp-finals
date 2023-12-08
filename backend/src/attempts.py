from pyauth.context import ctx
from pyauth.main import app


@app.get("/attempts")
async def get_attempts():
    return ctx.attempt_repo.get_many()
