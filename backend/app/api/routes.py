#
# # Berisi definisi endpoint API dan penanganan request/response.
#

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    File,
    Form,
    UploadFile,
    status,
    Body,
)
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.services import chat_service
from app.database import get_db, KnowledgeBase
from app import schemas
from app.utils.file_utils import save_uploaded_file
from typing import List, Dict, Any
import logging
import os
from fastapi.encoders import jsonable_encoder
from config import Config
from .auth import create_access_token, verify_token, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.utils.feature_utils import Feature
from uuid import UUID
from app.models.models import User, ChatFile

api = APIRouter()
kb = KnowledgeBase()

logger = logging.getLogger(__name__)


@api.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = await chat_service.login(db, form_data.username, form_data.password)
    if not user:
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


@api.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = await chat_service.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await chat_service.create_user(db, user)


@api.get("/user")
async def get_current_user(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    user = await chat_service.get_user_by_username(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api.delete("/chats/{chat_id}")
async def delete_chat_endpoint(
    chat_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = await chat_service.delete_chat(db, chat_id, current_user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"message": "Chat deleted successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.get("/user/{user_id}/chats")
async def get_user_chats(
    user_id: int, db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    try:
        chats = await chat_service.get_user_chats(db, user_id)
        return chats
    except HTTPException as he:
        raise he

    except Exception as e:
        logger.error(f"Error in get_user_chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.post("/chat/send")
async def send_chat_message(
    message: str = Form(...),
    file: UploadFile = File(None),
    user_id: int = Form(...),
    chat_id: UUID = Form(...),
    db: Session = Depends(get_db),
    feature: Feature = Feature.GENERAL,
):
    try:
        file_path = await save_uploaded_file(file) if file else None
        return await chat_service.process_chat_message(
            db, user_id, chat_id, message, feature, file_path
        )
    except Exception as e:
        logger.error(f"Error in send_chat_message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing chat message")


@api.get("/chat/{chat_id}/messages")
async def get_chat_messages(chat_id: str, db: Session = Depends(get_db)):
    """
    Endpoint untuk mengambil pesan-pesan dari chat tertentu.

    Args:
        chat_id (str): ID chat.

    Returns:
        List[Dict[str, str]]: Daftar pesan dalam chat, termasuk informasi file jika ada.
    """
    logging.info(f"Received request for messages of chat_id: {chat_id}")
    try:
        logging.info(f"Attempting to fetch messages for chat_id: {chat_id}")
        messages = await chat_service.get_chat_messages(UUID(chat_id))
        if not messages:
            logging.info(f"No messages found for chat_id: {chat_id}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"messages": [], "chat_id": chat_id},
            )
        for message in messages:
            if message.get("file_id"):
                file_info = (
                    db.query(ChatFile).filter(ChatFile.id == message["file_id"]).first()
                )
                logging.info(f"TES:{file_info}")

                if file_info:
                    message["file_name"] = file_info.file_name
                    message["file_path"] = file_info.file_path
                    message["file_url"] = (
                        f"/uploads/{os.path.basename(file_info.file_path)}"
                    )
        json_compatible_messages = jsonable_encoder(messages)
        logging.info(f"Returning {len(json_compatible_messages)} messages")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"messages": json_compatible_messages, "chat_id": chat_id},
        )
    except Exception as e:
        logger.error(f"Error in get_chat_messages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.post("/user/{user_id}/chats", response_model=schemas.ChatCreate)
async def create_new_chat(user_id: int, db: Session = Depends(get_db)):
    try:
        new_chat = await chat_service.create_new_chat(db, user_id)
        return new_chat
    except SQLAlchemyError as e:
        logger.error(f"Database error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")
    except ValueError as e:
        logger.error(f"Validation error creating chat: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@api.post("/knowledge_base/add")
async def add_knowledge_base_item(
    question: str = Form(...),
    answer: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        item = await chat_service.add_knowledge_base_item(db, question, answer, image)
        return {"message": "Item added successfully", "item": item}
    except Exception as e:
        logger.error(f"Error in add_knowledge_base_item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.get("/uploads/{file_path:path}")
async def get_file(file_path: str, current_user: User = Depends(get_current_user)):
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(f"uploads/{file_path}")
    except Exception as e:
        logger.error(f"Error in get_file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    # file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=404, detail="File not found")
    # return FileResponse(
    #     file_path, media_type="application/octet-stream", filename=filename
    # )
