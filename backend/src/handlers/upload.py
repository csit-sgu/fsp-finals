from fastapi import APIRouter, File, UploadFile
from uuid import uuid4
import aiofiles

import logging

upload_router = APIRouter()

logger = logging.getLogger("app")


@upload_router.post("/upload-file/")
async def create_upload_file(uploaded_file: UploadFile = File(...)):
    extension = uploaded_file.filename.split(".")[-1]
    file_name = uuid4()
    file_location = f"{file_name}.{extension}"
    try:
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await uploaded_file.read()  # async read
            await out_file.write(content)  # async write
        return {
            "info": f"File '{uploaded_file.filename}' saved at '{file_location}'"
        }
    except Exception as e:
        return {"error": f"Failed to save file: {e}"}
