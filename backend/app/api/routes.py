from fastapi import APIRouter, HTTPException, status, File, Form, UploadFile, Depends
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from app.services import chat_service
import logging
from app.utils.file_utils import save_uploaded_file
import os
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from app.database import KnowledgeBase, ChatManager, get_db
from config import Config
from fastapi.security import OAuth2PasswordRequestForm
from .auth import create_access_token, verify_token, verify_password, get_password_hash
from sqlalchemy.orm import Session
from .. import schemas
from app.models.models import User

load_dotenv()

api = APIRouter()

chat = ChatManager()
kb = KnowledgeBase()

UPLOAD_DIRECTORY = os.getenv("UPLOAD_FOLDER")
DEFAULT_USER = os.getenv("DEFAULT_USER", "1")


def safe_get(dict_obj, key, default=""):
    value = dict_obj[key]
    if value is None:
        return default
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


@api.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = chat.get_user(db, form_data.username)
    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@api.post("/logout")
async def logout(current_user: str = Depends(verify_token)):
    return {"message": "Successfully logged out"}


@api.get("/protected")
async def protected_route(current_user: str = Depends(verify_token)):
    return {"message": f"Hello, {current_user}!"}


@api.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    password = None
    db_user = chat.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    password = user.password
    hashed_password = get_password_hash(password)
    logging.info(f"Created user: {user.username} pass: {hashed_password}")
    return chat.create_user(db, user.username, hashed_password)


@api.post("/chat/send")
async def send_chat_message(
    message: str = Form(...),
    file: UploadFile = File(None),
    user_id: str = DEFAULT_USER,
    chat_id: int = Form(...),
):
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


@api.get("/user")
async def get_current_user(
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    # Ambil data user dari database berdasarkan username (current_user)
    user = chat.get_user(db, username=current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username}


@api.get("/chat/{chat_id}/messages")
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
        # logging.info(f"Retrieved messages: {messages}")

        if not messages:
            logging.info(f"No messages found for chat_id: {chat_id}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"messages": [], "chat_id": chat_id},
            )
        for message in messages:
            if message.get("file_path"):
                message["file_url"] = (
                    f"/uploads/{os.path.basename(message['file_path'])}"
                )
        json_compatible_messages = jsonable_encoder(messages)
        logging.info(f"Returning {len(json_compatible_messages)} messages")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"messages": json_compatible_messages, "chat_id": chat_id},
        )
    except Exception as e:
        logging.error(f"Error in get_chat_messages endpoint: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"},
        )


@api.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """
    Endpoint untuk mengambil file yang telah diunggah.

    Args:
        filename (str): Nama file yang diunggah.

    Returns:
        FileResponse: File yang diminta.
    """
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)
    logging.info(f"Attempting to access file: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File tidak ditemukan")
    logging.info(f"File found, returning: {file_path}")
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=filename
    )


@api.post("/files/upload")
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


@api.get("/user/{user_id}/chats")
async def get_user_chats(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil semua chat untuk pengguna tertentu.

    Args:
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        List[Dict]: Daftar semua chat dengan informasi id, title, dan created_at, userid
    """
    try:
        chats = chat_service.get_user_chats(user_id)
        return [
            {
                "chat_id": chat.id,
                "title": chat.title,
                "created_at": chat.created_at,
                "user_id": chat.user_id,
            }
            for chat in chats
        ]

    except Exception as e:
        logging.error(f"Error in get_user_chats endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.post("/user/{user_id}/chats")
async def create_new_chat(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint untuk membuat chat baru untuk pengguna tertentu.

    Args:
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        Dict: Informasi tentang chat baru yang dibuat.
    """
    try:
        new_chat = chat_service.create_new_chat(user_id=user_id)
        return {
            "id": new_chat["id"],
            "user_id": new_chat["user_id"],
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logging.error(f"Error in create_new_chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.delete("/user/{user_id}/chats")
async def delete_new_chat(user_id: str = DEFAULT_USER):
    """
    Endpoint untuk membuat chat baru untuk pengguna tertentu.

    Args:
        user_id (str): ID pengguna (default: DEFAULT_USER).

    Returns:
        Dict: Informasi tentang chat baru yang dibuat.
    """
    try:
        new_chat = chat_service.create_new_chat(user_id)
        return {
            "id": new_chat["id"],
            "user_id": new_chat["user_id"],
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logging.error(f"Error in delete_new_chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.post("/knowledge_base/add")
async def add_knowledge_base_item(
    question: str = Form(...), answer: str = Form(...), image: UploadFile = File(None)
):
    try:
        kb.add_item(question, answer, image)
        return {"message": "Item added successfully"}
    except Exception as e:
        logging.error(f"Error add knowledge_base : {str(e)}", exc_info=True)
        raise


@api.get("/uploads/knowledge_base_images/{filename}")
async def get_knowledge_base_image(filename: str):
    file_path = os.path.join(Config.IMAGE_UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Image not found")
    return FileResponse(file_path)
