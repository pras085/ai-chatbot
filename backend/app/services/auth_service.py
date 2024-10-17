from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config.config import Config
import bcrypt
import logging

from app.models import models
from app.services.user_service import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
logger = logging.getLogger(__name__)


def create_access_token(data: dict):
    try:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, Config.SECRET_KEY, algorithm=Config.ALGORITHM
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error during create access token : {e}")


def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def verify_password(plain_password, hashed_password):
    try:
        is_valid = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
        logger.info(f"Password valid: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"Error during password verification: {e}")


async def login(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Mengautentikasi pengguna berdasarkan username dan password.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        username (str): Username pengguna.
        password (str): Password pengguna.

    Returns:
        Optional[models.User]: Objek User jika autentikasi berhasil, None jika gagal.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal selama autentikasi.
    """
    try:
        user = await get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during authentication"
        )
