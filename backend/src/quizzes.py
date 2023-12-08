from context import ctx
from main import app

from shared.models import Quiz
from shared.routes import QuizRoutes


@app.get(QuizRoutes.QUIZ)
async def get_quizzes():
    return await ctx.quiz_repo.get_many()


@app.get(QuizRoutes.QUIZ + "/{id}")
async def get_quiz(id: int):
    return await ctx.quiz_repo.get_one(field="quiz_id", value=id)


@app.post(QuizRoutes.QUIZ)
async def add_quiz(quiz: Quiz):
    return await ctx.quiz_repo.add(quiz)
