from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from app.services import chat_service
import logging
from app.utils.file_utils import save_uploaded_file
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime


load_dotenv()

router = APIRouter()

UPLOAD_DIRECTORY = os.getenv("UPLOAD_FOLDER")
DEFAULT_USER = os.getenv("DEFAULT_USER", "1")


def safe_get(dict_obj, key, default=""):
    value = dict_obj[key]
    if value is None:
        return default
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


@router.post("/chat/send")
async def send_chat_message(
    message: str = Form(...),
    file: UploadFile = File(None),
    user_id: str = DEFAULT_USER,
    chat_id: int = Form(...),
):
    """
    Endpoint untuk mengirim pesan chat dan file opsional.

    Args:
        message (str): Pesan dari pengguna.
        file (UploadFile, optional): File yang diunggah oleh pengguna.
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        StreamingResponse: Stream respons dari model AI.
    """
    try:
        file_path = None
        if file:
            file_path = await save_uploaded_file(file)

        return StreamingResponse(
            chat_service.process_chat_message(user_id, chat_id, message, file_path),
            media_type="text/event-stream",
        )
    except Exception as e:
        logging.error(f"Error in send_chat_message endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat memproses pesan chat"
        )


@router.get("/chat/{chat_id}/messages")
async def get_chat_messages(chat_id: int):
    """
    Endpoint untuk mengambil pesan-pesan dari chat tertentu.

    Args:
        chat_id (int): ID chat.

    Returns:
        List[Dict[str, str]]: Daftar pesan dalam chat, termasuk informasi file jika ada.
    """
    logging.info(f"Received request for messages of chat_id: {chat_id}")
    try:
        logging.info(f"Attempting to fetch messages for chat_id: {chat_id}")
        messages = chat_service.get_chat_messages(chat_id)
        logging.info(f"Retrieved messages: {messages}")

        messages = chat_service.get_chat_messages(chat_id)
        if not messages:
            logging.info(f"No messages found for chat_id: {chat_id}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"messages": [], "chat_id": chat_id},
            )
        logging.info(f"Returning {len(messages)} messages")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"messages": messages, "chat_id": chat_id},
        )
    except Exception as e:
        logging.error(f"Error in get_chat_messages endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"},
        )


@router.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """
    Endpoint untuk mengambil file yang telah diunggah.

    Args:
        filename (str): Nama file yang diunggah.

    Returns:
        FileResponse: File yang diminta.
    """
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    return FileResponse(file_path)


@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint untuk mengunggah file.

    Args:
        file (UploadFile): File yang akan diunggah.

    Returns:
        dict: Informasi tentang file yang diunggah.
    """
    try:
        file_path = await save_uploaded_file(file)
        return {"filename": file.filename, "file_path": file_path}
    except Exception as e:
        logging.error(f"Error in upload_file endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat mengunggah file"
        )


@router.get("/user/{user_id}/chats")
async def get_user_chats(user_id: str = DEFAULT_USER) -> List[Dict[str, str]]:
    """
    Endpoint untuk mengambil semua chat untuk pengguna tertentu.

    Args:
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        List[Dict]: Daftar semua chat dengan informasi id, title, dan created_at.
    """
    try:
        chats = chat_service.get_user_chats(user_id)

        response = [
            {
                "chat_id": safe_get(chat, "id"),
                "title": safe_get(chat, "title"),
                "created_at": safe_get(chat, "created_at"),
                "user_id": safe_get(chat, "user_id"),
            }
            for chat in chats
        ]
        return response
    except Exception as e:
        logging.error(f"Error in get_user_chats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/user/{user_id}/chats")
async def create_new_chat(user_id: str = DEFAULT_USER):
    """
    Endpoint untuk membuat chat baru untuk pengguna tertentu.

    Args:
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        Dict: Informasi tentang chat baru yang dibuat.
    """
    try:
        new_chat = chat_service.create_new_chat(user_id)
        return new_chat
    except Exception as e:
        logging.error(f"Error in create_new_chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
