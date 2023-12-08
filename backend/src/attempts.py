from context import ctx
from main import app


@app.get("/attempts")
async def get_attempts():
    return await ctx.attempt_repo.get_many()
