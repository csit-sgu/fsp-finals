import logging
from fastapi import APIRouter
from typing import Annotated
from fastapi import Depends
from deps import get_current_user
from context import ctx

from shared.entities import User, RunningContainer
from docker_api import get_client, run_container
from shared.models import ContainerRequest

from datetime import datetime

container_router = APIRouter()
log = logging.getLogger("app")


@container_router.post("/container/{quiz_id}", summary="Get started container for quiz")
async def get_container(
    user: Annotated[User, Depends(get_current_user)], request: ContainerRequest
):
    client = get_client(user.id)
    container_id = run_container(client, **request.payload.model_dump())

    entity = RunningContainer(
        container_id=container_id,
        user_id=user.id,
        block_id=request.block_id,
        start_timestamp=datetime.now(),
        base_url=client.api.base_url,
    )
    await ctx.container_repo.add(entity)

    return container_id
