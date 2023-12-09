from context import ctx
from fastapi import APIRouter
import json
from typing import Annotated
from deps import get_current_user

from context import ctx
from fastapi import APIRouter, Depends, HTTPException

from shared.entities import User
from shared.models import (
    AttemptFrontend,
    BlockType,
)
import shared.entities as entities
import logging

attempt_router = APIRouter()
log = logging.getLogger("app")


@attempt_router.get("/attempts")
async def get_attempts():
    return await ctx.attempt_repo.get_many()


@attempt_router.post("/attempt")
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
            answer.answer = [answer.answer]

        for ans in answer.answer:
            chosen_option = options[ans.strip()]
            if chosen_option is None:
                continue
            total_score += chosen_option["score"]

    return total_score
