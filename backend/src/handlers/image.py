from fastapi import APIRouter, File, UploadFile
from uuid import uuid4
import aiofiles
from pathlib import Path

import logging

image_router = APIRouter()

logger = logging.getLogger("app")


@image_router.post("/image/")
async def upload_image(image: UploadFile = File(...)):
    extension = image.filename.split(".")[-1]

    try:
        dir_path = Path("static/")
        dir_path.mkdir(parents=True, exist_ok=True)

        file_name = uuid4()
        file_location = f"static/{file_name}.{extension}"
        async with aiofiles.open(file_location, "wb") as out_file:
            content = await image.read()
            await out_file.write(content)
        return {
            "info": f"File '{image.filename}' saved at '{file_location}'"
        }
    except Exception as e:
        return {"error": f"Failed to save file: {e}"}
