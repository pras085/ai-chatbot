import logging
import os
from typing import List, Dict, Any
from uuid import UUID

from fastapi import Depends, HTTPException, Form, UploadFile, File, APIRouter
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from app import schemas
from app.config.database import get_db
from app.models.jwt import JwtUser
from app.models.models import ChatFile
from app.services import chat_service, prompt_service
from app.services.auth_service import verify_token
from app.utils.feature_utils import Feature

chat_routes = APIRouter()

logger = logging.getLogger(__name__)

@chat_routes.delete("/chats/{chat_id}")
async def delete_chat_endpoint(
    chat_id: UUID,
    current_user: JwtUser = Depends(verify_token),
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


@chat_routes.get("/user/{user_id}/chats")
async def get_user_chats(
    db: Session = Depends(get_db),
    feature: Feature = Feature.GENERAL,
    user_id: int = 0, # unused
    current_user: JwtUser = Depends(verify_token),
) -> List[Dict[str, Any]]:
    logger.info(f"Attempting to fetch chats for user_id: {current_user.id}")
    try:
        chats = await chat_service.get_user_chats(db, current_user.id, feature)
        logger.info(f"Successfully fetched {len(chats)} chats for user_id: {current_user.id}")
        return chats
    except HTTPException as he:
        logger.error(f"HTTP exception in get_user_chats: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Error in get_user_chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@chat_routes.post("/chat/send")
async def send_chat_message(
    message: str = Form(...),
    files: List[UploadFile] = File(None),  # Banyak file
    chat_id: UUID = Form(...),
    db: Session = Depends(get_db),
    feature: Feature = Feature.GENERAL,
    current_user: JwtUser = Depends(verify_token),
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

        return await prompt_service.process_chat_message(
            db,
            current_user.id,
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


@chat_routes.get("/chat/{chat_id}/messages")
async def get_chat_messages(
        chat_id: str,
        db: Session = Depends(get_db),
        current_user: JwtUser = Depends(verify_token),
):
    """
    Endpoint untuk mengambil pesan-pesan dari chat tertentu.

    Args:
        current_user:
        db:
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


@chat_routes.post("/user/{user_id}/chats", response_model=schemas.ChatCreate)
async def create_new_chat(
        user_id: int,
        db: Session = Depends(get_db),
        feature: Feature = Feature.GENERAL,
        current_user: JwtUser = Depends(verify_token),
):
    try:
        new_chat = await chat_service.create_new_chat(db, current_user.id, feature)
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


@chat_routes.get("/uploads/{file_path:path}")
async def get_file(
        file_path: str,
        current_user: JwtUser = Depends(verify_token)
):
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
