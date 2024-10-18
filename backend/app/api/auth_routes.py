from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import app.services.user_service
from app import schemas
from app.config.database import get_db
from app.models.jwt import JwtUser
from app.services.auth_service import create_access_token, verify_token

auth_routes = APIRouter()


@auth_routes.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = await app.services.auth_service.login(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data=JwtUser(user.username, user.id, 'user').dict())
    return {"access_token": access_token, "token_type": "bearer"}


@auth_routes.post("/logout")
async def logout(
        current_user: JwtUser = Depends(verify_token)
):
    return {"message": "Successfully logged out"}


@auth_routes.post("/register", response_model=schemas.User)
async def register(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    db_user = await app.services.user_service.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await app.services.user_service.create_user(db, user)
