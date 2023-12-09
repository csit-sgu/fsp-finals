import json
from typing import Dict, Annotated
from uuid import uuid4, UUID
from deps import get_current_user

from context import ctx
from fastapi import APIRouter, Depends, HTTPException

from shared.entities import User, Quiz, QuizComplexity
from shared.models import (
    Block,
    QuizFrontend,
    BlockType,
    BlockFrontend,
)
import logging

quiz_router = APIRouter()
log = logging.getLogger("app")


@quiz_router.get("/quiz", summary="Get quiz using filters if needed")
async def get_quizzes(
    age_group: str | None = None,
    category: str | None = None,
    complexity: int | None = None,
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
async def get_quiz(id: UUID):
    quiz = await ctx.quiz_repo.get_one(field="quiz_id", value=id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@quiz_router.post("/quiz", status_code=201)
async def create_quiz(
    user: Annotated[User, Depends(get_current_user)], quiz: QuizFrontend
) -> UUID:
    if not user.is_admin:
        raise HTTPException(
            status_code=403, detail="Only admins can create new quizzes"
        )

    if user.username != quiz.author_username:
        raise HTTPException(
            status_code=403, detail="Quiz autor does not match current user"
        )

    ids = dict((b.block_id, str(uuid4())) for b in quiz.blocks)
    blocks = list(map(encode_block(ids), quiz.blocks))
    await ctx.block_repo.add(blocks)

    quiz_id = uuid4()

    q = Quiz(
        quiz_id=quiz_id,
        title=quiz.title,
        author_id=user.id,
        description=quiz.description,
        is_paid=True,
        category=quiz.category,
        entry_id=blocks[0].block_id,
        is_for_subs=quiz.is_for_subs
    )

    await ctx.quiz_repo.add(q)

    await ctx.complexity_repo.add(
        QuizComplexity(
            quiz_id=quiz_id,
            complexity=quiz.complexity,
            age_group=quiz.age_group,
        )
    )

    return quiz_id


def encode_block(ids: Dict):
    def encode_block_inner(block: BlockFrontend):
        match block.block_type:
            case BlockType.CASE:
                options = block.payload["options"]
                for opt in options:
                    if options[opt].get("next_block"):
                        options[opt]["next_block"] = ids[
                            options[opt]["next_block"]
                        ]
            case _:
                if block.payload.get("next_block"):
                    block.payload["next_block"] = ids[
                        block.payload["next_block"]
                    ]
        return Block(
            block_id=ids[block.block_id],
            block_type=block.block_type,
            problem=block.problem,
            payload=json.dumps(block.payload),
        )

    return encode_block_inner
