import json
from typing import Dict, List, Annotated
from uuid import uuid4, UUID
from deps import get_current_user

from context import ctx
from fastapi import APIRouter, Depends, HTTPException

from shared.entities import User, Quiz, QuizComplexity
from shared.models import (
    Block,
    QuizFrontend,
    AttemptFrontend,
    BlockType,
    BlockFrontend,
)
import shared.entities as entities
import logging

quiz_router = APIRouter()
log = logging.getLogger("app")


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

    return quiz_id


def encode_block(ids: Dict):
    def encode_block_inner(block: BlockFrontend):
        match block.block_type:
            case BlockType.CASE:
                options = block.payload["options"]
                for opt in options:
                    if options[opt]["next_block"] is not None:
                        options[opt]["next_block"] = ids[
                            options[opt]["next_block"]
                        ]
            case _:
                if block.payload["next_block"] is not None:
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


@quiz_router.post("/attempt")
async def make_attempt(
    user: Annotated[User, Depends(get_current_user)], attempt: AttemptFrontend
):
    if attempt.username != user.username:
        raise HTTPException(
            status_code=403,
            detail="Trying to submit attempt for another user",
        )

    quiz = await ctx.quiz_repo.get_one("quiz_id", attempt.quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    total_score = 0
    for answer in attempt.answers:
        original_block: entities.Block | None = await ctx.block_repo.get_one(
            "block_id", answer.block_id
        )
        if original_block is None:
            log.warn(f"Block {answer.block_id} not found")
            continue

        options = json.loads(original_block.payload)["options"]
        if (
            original_block.block_type == BlockType.MULTIPLE_CHOICE
            and type(answer.answer) != list
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Expected list of answers in {original_block.block_id}",
            )
        if (
            original_block.block_type != BlockType.MULTIPLE_CHOICE
            and type(answer.answer) == list
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Expected single answer in {original_block.block_id}",
            )

        if type(answer.answer) != list:
            answer.answer = list(answer.answer)

        for ans in answer.answer:
            chosen_option = options[ans.strip()]
            if chosen_option is None:
                continue
            total_score += chosen_option["score"]

    return total_score
