import logging
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from deps import get_current_user
from context import ctx

from shared.entities import User
from docker_api import get_client, run_container, execute_command
from shared.models import ContainerRequest
from fastapi import HTTPException

from datetime import datetime
from uuid import UUID
import json

container_router = APIRouter()
log = logging.getLogger("app")


@container_router.post(
    "/container/{block_id}", summary="Deploy a new container for a block"
)
async def get_container(
    user: Annotated[User, Depends(get_current_user)],
    block_id: UUID,
    request: ContainerRequest,
):
    container = ctx.container_repo.get(user.id, block_id)
    if container:
        log.warn("User made attempt to create another container for this block")
        log.info(f"Got existing container for user {user.id}: {container}")
        raise HTTPException(status_code=400)

    client = get_client(user.id, block_id)
    container_id = run_container(client, **request.payload.model_dump())

    entity = {
        "container_id": container_id,
        "start_timestamp": datetime.now().strftime("%Y-%m-%d, %H-%M-%S"),
        "base_url": client.api.base_url,
    }
    ctx.container_repo.add_or_update(user.id, block_id, entity)

    return container_id


@container_router.post(
    "/container/{block_id}/validate", summary="Validate an answer submitted by a user"
)
async def submit_answer(
    user: Annotated[User, Depends(get_current_user)], block_id: UUID, answer: str
):
    container = ctx.container_repo.get(user.id, block_id)

    if not container:
        log.warn("User made attempt to submit answer on expired container")
        raise HTTPException(status_code=400)

    block = await ctx.block_repo.get_one("block_id", block_id)
    expected_output = (json.loads(block.payload))["expected_output"]

    client = list(
        filter(lambda x: x[1].api.base_url == container["base_url"], ctx.docker_pool)
    )[0][1]

    result = execute_command(client, container["container_id"], answer)

    return result.output.decode("utf-8").strip() == expected_output.strip()
