#
# # Berisi definisi endpoint API dan penanganan request/response.
#

from fastapi import APIRouter, HTTPException, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from app.services import chat_service
from app.repositories import get_db
from app.repositories.knowledge_base import knowledge_manager
from app import schemas
from app.utils.file_utils import save_uploaded_file
from typing import List, Dict, Any
import logging
import os
from fastapi.encoders import jsonable_encoder
from .auth import create_access_token, verify_token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from app.utils.feature_utils import Feature
from uuid import UUID
from app.models.models import User, ChatFile


api = APIRouter()

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
    logger.info(f"Attempting to fetch chats for user_id: {user_id}")
    try:
        chats = await chat_service.get_user_chats(db, user_id)
        logger.info(f"Successfully fetched {len(chats)} chats for user_id: {user_id}")
        return chats
    except HTTPException as he:
        logger.error(f"HTTP exception in get_user_chats: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error in get_user_chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@api.post("/chat/send")
async def send_chat_message(
    message: str = Form(...),
    files: List[UploadFile] = File(None),  # Banyak file
    user_id: int = Form(...),
    chat_id: UUID = Form(...),
    db: Session = Depends(get_db),
    feature: Feature = Feature.GENERAL,
):
    try:
        file_contents = []
        if files:
            for file in files:
                content = await file.read()
                file_contents.append(
                    {
                        "name": file.filename,
                        "content": content.decode("utf-8", errors="ignore"),
                    }
                )
                # Simpan file jika diperlukan
                # file_path = await save_uploaded_file(file)
                # chat_manager.add_file_to_chat(db, chat_id, file.filename, file_path)

        return await chat_service.process_chat_message(
            db,
            user_id,
            chat_id,
            message,
            feature,
            file_contents,
        )
    except ValueError as e:
        logger.error(f"File upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"File upload error: {str(e)}")
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


@api.post("/context")
async def upload_context(
    text: str = Form(None),
    file: UploadFile = File(None),
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        user = await chat_service.get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if text:
            context = knowledge_manager.add_context(db, user.id, text, "text")
        elif file:
            file_path = await save_uploaded_file(file)
            context = knowledge_manager.add_context(
                db, user.id, file.filename, "file", file_path
            )
        else:
            raise HTTPException(
                status_code=400, detail="Either text or file must be provided"
            )

        return {
            "message": "Context uploaded successfully",
            "context_id": str(context.id),
        }
    except Exception as e:
        logger.error(f"Error uploading context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/context")
async def get_context(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        user = await chat_service.get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        context = knowledge_manager.get_latest_context(db, user.id)
        if not context:
            return {"message": "No context found"}
        return {
            "id": str(context.id),
            "content": context.content,
            "content_type": context.content_type,
            "file_path": context.file_path,
            "updated_at": context.updated_at,
        }
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api.get("/contexts")
async def get_all_contexts(
    current_user: User = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        user = await chat_service.get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        contexts = knowledge_manager.get_user_contexts(db, user.id)
        return [
            {
                "id": str(c.id),
                "content": c.content,
                "content_type": c.content_type,
                "updated_at": c.updated_at,
            }
            for c in contexts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.delete("/context/{context_id}")
async def delete_context(
    context_id: UUID,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        user = await chat_service.get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        success = knowledge_manager.delete_context(db, context_id, user.id)
        if success:
            return {"message": "Context deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Context not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
