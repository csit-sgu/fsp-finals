import json
from typing import List, Annotated
from uuid import uuid4
from deps import get_current_user

from context import ctx
from fastapi import APIRouter, Depends, HTTPException

from shared.entities import User, Quiz, QuizComplexity
from shared.models import Block, QuizFrontend, Attempt

quiz_router = APIRouter()


@quiz_router.get("/quiz", summary="Get quiz using filters if needed")
async def get_quizzes(
    age_group: str | None = None,
    category: str | None = None,
    complexity: str | None = None,
):
    filters = dict()
    if age_group is not None:
        filters["age_group"] = age_group

    if category is not None:
        filters["category"] = category

    if complexity is not None:
        filters["complexity"] = complexity
    return await ctx.quiz_info_repo.get_many_filtered(filters)


@quiz_router.get("/quiz/{id}")
async def get_quiz(id: int):
    return await ctx.quiz_repo.get_one(field="quiz_id", value=id)


@quiz_router.post("/quiz", status_code=201)
async def create_quiz(quiz: QuizFrontend):
    author: User = await ctx.user_repo.get_one(
        "username", quiz.author_username
    )
    ids = dict((b.block_id, str(uuid4())) for b in quiz.blocks)
    blocks: List[Block] = list(
        map(
            lambda b: Block(
                block_id=ids[b.block_id],
                block_type=b.block_type,
                payload=json.dumps(b.payload),
            ),
            quiz.blocks,
        )
    )
    await ctx.block_repo.add(blocks)

    quiz_id = uuid4()

    q = Quiz(
        quiz_id=quiz_id,
        title=quiz.title,
        author_id=str(author.id),
        description=quiz.description,
        category=quiz.category,
        entry_id=blocks[0].block_id,
    )

    await ctx.quiz_repo.add(q)

    await ctx.complexity_repo.add(
        QuizComplexity(
            quiz_id=quiz_id,
            complexity=quiz.complexity,
            age_group=quiz.age_group,
        )
    )


@quiz_router.post("/attempt")
async def make_attempt(
    user: Annotated[User, Depends(get_current_user)], attempt: Attempt
):
    if attempt.username != user.username:
        raise HTTPException(
            status_code=403,
            detail="Trying to submit attempt for another user",
        )
    pass
