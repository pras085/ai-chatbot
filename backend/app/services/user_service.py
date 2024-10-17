from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.models import models
from app.utils.auth_utils import get_password_hash
from app.services.chat_service import chat_manager, logger


async def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Mengambil data pengguna berdasarkan username.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        username (str): Username pengguna yang dicari.

    Returns:
        Optional[models.User]: Objek User jika ditemukan, None jika tidak ditemukan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat mengambil data pengguna.
    """
    try:
        return chat_manager.get_user(db, username)
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user"
        )


async def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Membuat pengguna baru.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        user (schemas.UserCreate): Data pengguna untuk dibuat.

    Returns:
        models.User: Objek User yang baru dibuat.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat membuat pengguna.
    """
    try:
        hashed_password = get_password_hash(user.password)
        return chat_manager.create_user(db, user.username, hashed_password)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while creating user"
        )
