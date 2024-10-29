from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import app.services.user_service
from app import schemas
from app.config.database import get_db
from app.models.jwt import JwtUser
from app.services.auth_service import verify_token

user_routes = APIRouter()


@user_routes.get("/user")
async def get_current_user(
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = await app.services.user_service.get_user_by_username(db, current_user.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_routes.get("/users")
async def get_all_users(
    current_user: JwtUser = Depends(verify_token),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = await app.services.user_service.get_users(db, skip, limit)
    return users


@user_routes.get("/user/{user_id}")
async def get_user_by_id(
    user_id: int,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = await app.services.user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_routes.delete("/user/{user_id}")
async def delete_user_by_id(
    user_id: int,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = await app.services.user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await app.services.user_service.delete_user(db, user)


@user_routes.put("/user/{user_id}")
async def update_user_by_id(
    user_id: int,
    user_update: schemas.UserCreateUpdate,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = await app.services.user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await app.services.user_service.update_user(db, user, user_update)

@user_routes.post("/user")
async def create_user(
    user: schemas.UserCreateUpdate,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await app.services.user_service.create_user(
        db,
        user
    )