import json
import asyncio
from typing import Annotated, List
from deps import get_current_user
import datetime

from context import ctx
from fastapi import APIRouter, Depends, HTTPException

from shared.entities import User
from shared.models import (
    AttemptFrontend,
    AttemptFeedback,
    Attempt,
    BlockType,
)
import shared.entities as entities
import logging

attempt_router = APIRouter()
log = logging.getLogger("app")


@attempt_router.get("/attempts")
async def get_attempts():
    return await ctx.attempt_repo.get_many()


async def make_attempt_helper(is_subscriber, answer, overall_feedback, total_score):
    original_block: entities.Block | None = await ctx.block_repo.get_one(
        "block_id", answer.block_id
    )
    if not original_block:
        log.warn(f"Block {answer.block_id} not found")
        return

    options = json.loads(original_block.payload)["options"]
    if (
        original_block.block_type == BlockType.MULTIPLE_CHOICE
        and not isinstance(answer.answer, list)
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Expected list of answers in {original_block.block_id}",
        )
    if original_block.block_type != BlockType.MULTIPLE_CHOICE and isinstance(
        answer.answer, list
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Expected single answer in {original_block.block_id}",
        )

    if not isinstance(answer.answer, list):
        answer.answer = [answer.answer]

    prompt_block_str = f"Вопрос: {original_block.problem}"
    if original_block.block_type == BlockType.FREE_ANSWER:
        prompt_block_str += f"\nЯ ответил {answer.answer}. Объясни, правильный ли это ответ и почему."
    elif original_block.block_type == BlockType.MULTIPLE_CHOICE:
        prompt_block_str += f'\nВарианты ответа: {", ".join(options.keys())}'
        prompt_block_str += f'\nЯ ответил {", ".join(answer.answer)}. Объясни, правильный ли это ответ и почему.'
    else:
        prompt_block_str += f'\nВарианты ответа: {", ".join(options.keys())}'
        prompt_block_str += f"\nЯ ответил {answer.answer}. Объясни, правильный ли это ответ и почему."

    block_score = 0
    for ans in answer.answer:
        try:
            chosen_option = options[ans.strip()]
        except KeyError:
            continue
        block_score += chosen_option["score"]

    total_score += block_score

    completion = ""
    if block_score < 1 and is_subscriber:
        completion = (
            (
                await ctx.openai_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_block_str,
                        }
                    ],
                    model="gpt-4",
                )
            )
            .choices[0]
            .message.content
        )

    correctness = 0
    if block_score >= 1:
        correctness = 2
    elif block_score > 0:
        correctness = 1

    attempt_feedback = AttemptFeedback(
        block_id=answer.block_id,
        feedback=completion,
        correctness=correctness,
        score=block_score,
    )

    return attempt_feedback


@attempt_router.post("/attempt")
async def make_attempt(
    user: Annotated[User, Depends(get_current_user)],
    attempt_frontend: AttemptFrontend,
):
    if attempt_frontend.username != user.username:
        raise HTTPException(
            status_code=403,
            detail="Trying to submit attempt for another user",
        )

    quiz = await ctx.quiz_repo.get_one("quiz_id", attempt_frontend.quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")

    overall_feedback: List[AttemptFeedback] = list()
    total_score = 0
    batch = [
        make_attempt_helper(user.is_subscriber, answer, overall_feedback, total_score)
        for answer in attempt_frontend.answers
    ]

    res = await asyncio.gather(*batch)

    attempt = Attempt(
        quiz_id=attempt_frontend.quiz_id,
        user_id=user.id,
        quiz_score=total_score,
        time_passed=69,
        start_timestamp=datetime.date(1970, 1, 1),
    )
    await ctx.attempt_repo.add(attempt)
    log.warn("Added attempt")

    return res
