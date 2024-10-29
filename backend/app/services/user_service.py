import logging
from typing import Optional, Type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.models import models
from app.models.models import User
from app.repositories.user_manager import UserManager
from app.utils.auth_utils import get_password_hash

user_manager = UserManager()
logger = logging.getLogger(__name__)

async def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    try:
        return user_manager.get_user(db, username)
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user"
        )


async def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[Type[User]]:
    try:
        return user_manager.get_users(db, skip, limit)
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching users"
        )


async def create_user(db: Session, user: schemas.UserCreateUpdate) -> models.User:
    try:
        hashed_password = get_password_hash(user.password)
        return user_manager.create_user(db, user.username, hashed_password)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while creating user"
        )


async def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    try:
        return user_manager.get_user_by_id(db, user_id)
    except Exception as e:
        logger.error(f"Error getting user by id: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching user"
        )


async def update_user(db: Session, user: models.User, user_update: schemas.UserCreateUpdate) -> models.User:
    try:
        user_update.password = get_password_hash(user_update.password)
        return user_manager.update_user(db, user, user_update.model_dump(exclude_unset=True))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while updating user"
        )


async def delete_user(db: Session, user: models.User) -> bool:
    try:
        return user_manager.delete_user(db, user)
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while deleting user"
        )