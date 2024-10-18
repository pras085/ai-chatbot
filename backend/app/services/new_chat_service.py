import traceback
from typing import Dict, Any
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config.config import Config
from app.config.database import SessionLocal
from app.models import models
from app.repositories.chat_manager import ChatManager
from app.services.knowledge_base_service import logger
from app.utils.feature_utils import Feature

CLAUDE_API_KEY = Config.CLAUDE_API_KEY
if not CLAUDE_API_KEY:
    logger.error("CLAUDE_API_KEY is not set")
    raise ValueError("CLAUDE_API_KEY is not set")
MODEL_NAME = Config.MODEL_NAME

chat_manager = ChatManager()


async def get_user_chats(db: Session, user_id: int, feature: Feature = Feature.GENERAL) -> List[Dict[str, Any]]:
    """
    Mengambil daftar chat untuk pengguna tertentu.

    Args:
        feature:
        db (Session): Sesi repositories SQLAlchemy.
        user_id (int): ID pengguna.

    Returns:
        List[models.Chat]: Daftar objek Chat milik pengguna.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil daftar chat.
    """
    try:
        chats = chat_manager.get_user_chats(db, user_id, feature)
        return [
            {
                "chat_id": str(chat.id),
                "title": chat.title,
                "created_at": chat.created_at.isoformat(),
                "user_id": str(chat.user_id),
            }
            for chat in chats
        ]
    except Exception as e:
        logger.error(f"Error getting user chats: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user chats"
        )


async def is_first_message(chat_id: UUID) -> bool:
    """
    Memeriksa apakah ini adalah pesan pertama dalam chat.

    Args:
        chat_id (int): ID chat yang akan diperiksa.

    Returns:
        bool: True jika ini adalah pesan pertama, False jika bukan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat memeriksa pesan.
    """
    try:
        messages = await get_chat_messages(chat_id)
        return len(messages) == 0
    except Exception as e:
        logger.error(f"Error checking if first message: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while checking message"
        )


async def get_chat_messages(chat_id: UUID) -> List[dict]:
    """
    Mengambil semua pesan untuk chat tertentu.

    Args:
        chat_id (int): ID chat yang pesannya akan diambil.

    Returns:
        List[dict]: Daftar pesan dalam format dictionary.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil pesan chat.
    """
    db = SessionLocal()
    try:
        return chat_manager.get_chat_messages(db, chat_id)
    except Exception as e:
        logger.error(f"Error getting chat messages: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching chat messages"
        )


async def create_new_chat(db: Session, user_id: int, feature: Feature = Feature.GENERAL) -> dict:
    """
    Membuat chat baru untuk pengguna tertentu.

    Args:
        feature:
        db (Session): Sesi repositories SQLAlchemy.
        user_id (int): ID pengguna yang membuat chat.

    Returns:
        models.Chat: Objek Chat yang baru dibuat.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat membuat chat baru.
    """
    try:
        new_chat = chat_manager.create_chat(db, user_id, feature)
        return {
            "id": str(new_chat.id),
            "title": new_chat.title,
            "user_id": new_chat.user_id,
        }
    except Exception as e:
        logger.error(f"Error creating new chat: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while creating new chat"
        )


async def update_chat_title(db: Session, chat_id: UUID, title: str) -> bool:
    """
    Memperbarui judul chat.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        chat_id (int): ID chat yang akan diperbarui.
        title (str): Judul baru untuk chat.

    Returns:
        bool: True jika berhasil diperbarui, False jika tidak.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat memperbarui judul chat.
    """
    try:
        return chat_manager.update_chat_title(db, chat_id, title)
    except Exception as e:
        logger.error(f"Error updating chat title: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while updating chat title"
        )


async def delete_chat(db: Session, chat_id: UUID, user_id: int):
    """
    Menghapus chat berdasarkan ID.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        chat_id (int): ID chat yang akan dihapus.

    Returns:
        bool: True jika berhasil dihapus, False jika tidak.
    """
    # Panggil fungsi di chat_manager untuk menghapus chat
    try:
        # Panggilan ke chat_manager.delete_chat dengan argumen yang benar
        success = chat_manager.delete_chat(db, chat_id, user_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Chat not found or you don't have permission to delete it",
            )
        return {"status": "success", "message": "Chat deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting chat: {str(e)}")
        logger.error(traceback.format_exc())  # Menambahkan traceback ke log
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_latest_chat_id(db: Session, user_id: int) -> Optional[UUID]:
    """
    Mendapatkan ID chat terbaru untuk pengguna tertentu.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        user_id (int): ID pengguna.

    Returns:
        Optional[int]: ID chat terbaru, atau None jika tidak ada.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil ID chat terbaru.
    """
    try:
        return chat_manager.get_latest_chat_id(db, user_id)
    except Exception as e:
        logger.error(f"Error getting latest chat ID: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching latest chat ID",
        )
