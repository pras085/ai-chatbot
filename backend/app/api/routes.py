import os
import shutil
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from app.services.chat_service import chat_with_retry_stream
from app.services.file_service import save_uploaded_file
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    message: str = Form(...),
    file: UploadFile = File(None),
    user_id: str = Depends(lambda: "DEFAULT_USER"),
):
    """
    Endpoint untuk menerima pesan chat dan file opsional.

    Args:
        message (str): Pesan dari pengguna.
        file (UploadFile, optional): File yang diunggah oleh pengguna.

    Returns:
        StreamingResponse: Stream respons dari model AI.
    """
    try:
        file_info = None
        if file:
            directory = "./uploads"
            os.makedirs(directory, exist_ok=True)
            file_path = f"{directory}/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_info = f"File attached: {file.filename} (size: {os.path.getsize(file_path)} bytes)"

        full_message = f"{message}\n\n{file_info}" if file_info else message

        return StreamingResponse(
            chat_with_retry_stream(user_id, full_message),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat memproses permintaan Anda"
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file.

    Args:
        file (UploadFile): File yang akan diunggah.

    Returns:
        dict: Informasi tentang file yang diunggah.
    """
    file_path = await save_uploaded_file(file)
    return {"filename": file.filename, "file_path": file_path}
