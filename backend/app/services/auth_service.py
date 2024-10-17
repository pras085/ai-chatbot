from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config.config import Config
import bcrypt
import logging


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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


def get_password_hash(password):
    try:
        salt = bcrypt.gensalt(14)
        hashed = bcrypt.hashpw(password=password.encode(), salt=salt)
        return hashed.decode()
    except Exception as e:
        logger.error(f"Error during get password hash: {e}")
