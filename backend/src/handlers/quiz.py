from typing import List
from uuid import UUID, uuid4

from context import ctx
from fastapi import APIRouter

from shared.models import Block, Quiz, QuizFrontend

quiz_router = APIRouter()


@quiz_router.get("/quiz")
async def get_quizzes():
    return await ctx.quiz_repo.get_many()


@quiz_router.get("/quiz/{id}")
async def get_quiz(id: UUID):
    return await ctx.quiz_repo.get_one(field="quiz_id", value=id)


@quiz_router.post("/quiz")
async def create_quiz(quiz: QuizFrontend):
    ids = dict((b.block_id, str(uuid4())) for b in quiz.blocks)
    blocks: List[Block] = list(
        map(
            lambda b: Block(
                block_id=ids[b.block_id],
                block_type=b.block_type,
                payload=b.payload,
            ),
            quiz.blocks,
        )
    )
    await ctx.block_repo.add(blocks)

    q = Quiz(
        title=quiz.title,
        author_id=quiz.author_id,
        description=quiz.description,
        category=quiz.category,
        entry_id=blocks[0],
    )
    await ctx.quiz_repo.add(q)
