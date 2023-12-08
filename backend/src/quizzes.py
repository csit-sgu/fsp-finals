from typing import Optional
from context import ctx
from shared.models import Quiz, Block
from main import app
from shared.routes import QuizRoutes
from fastapi import HTTPException

import containers


@app.get(QuizRoutes.QUIZ)
async def get_quizzes():
    return await ctx.quiz_repo.get_many()


@app.get(QuizRoutes.QUIZ + "/{id}")
async def get_quiz(id: int):
    return await ctx.quiz_repo.get_one(field="quiz_id", value=id)


@app.post(QuizRoutes.QUIZ)
async def add_quiz(quiz: Quiz):
    return await ctx.quiz_repo.add(quiz)


@app.post(QuizRoutes.QUIZ + "/{id}/container/start")
async def start_container(quiz_id: int):
    quiz: Optional[Quiz] = ctx.quiz_repo.get_one(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    block: Optional[Block] = ctx.block_repo.get_one(quiz.entry_id)
    if block is None:
        raise HTTPException(status_code=404, detail="Container not found")

    containers.build_image(block.payload["dockerfile"], quiz.title.replace(' ', '_'))