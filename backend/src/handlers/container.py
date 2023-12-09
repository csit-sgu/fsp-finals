import logging
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from deps import get_current_user
from context import ctx

from shared.entities import User
from docker_api import get_client, run_container, execute_command, stop_container
from shared.models import ContainerRequest, ValidateRequest
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
    container = await ctx.container_repo.get(user.id, block_id)
    if container:
        message = "User made attempt to create another container for this block"
        log.warn(message)
        log.info(f"Got existing container for user {user.id}: {container}")
        raise HTTPException(status_code=400, detail=message)

    client = get_client(user.id, block_id)
    container_id = run_container(client, **request.payload.model_dump())

    entity = {
        "container_id": container_id,
        "start_timestamp": datetime.now().strftime("%Y-%m-%d, %H-%M-%S"),
        "base_url": client.api.base_url,
    }

    await ctx.container_repo.add_or_update(
        user.id, block_id, entity, ttl=request.payload.ttl
    )

    return container_id


@container_router.post(
    "/container/{block_id}/validate", summary="Validate an answer submitted by a user"
)
async def submit_answer(
    user: Annotated[User, Depends(get_current_user)],
    block_id: UUID,
    request: ValidateRequest,
):
    container = await ctx.container_repo.get(user.id, block_id)

    if not container:
        message = "User made attempt to submit answer on expired container"
        log.warn(message)
        raise HTTPException(status_code=400, detail=message)

    block = await ctx.block_repo.get_one("block_id", block_id)
    expected_output = (json.loads(block.payload))["expected_output"]

    client = list(
        filter(lambda x: x[1].api.base_url == container["base_url"], ctx.docker_pool)
    )[0][1]

    result = execute_command(client, container["container_id"], request.answer)

    await stop_container(client, container["container_id"])
    await ctx.container_repo.remove(user.id, block_id)

    return result.output.decode("utf-8").strip() == expected_output.strip()
