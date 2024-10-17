from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import app.services.user_service
from app.repositories.database import get_db
from app.services.auth_service import verify_token

user_routes = APIRouter()


@user_routes.get("/user")
async def get_current_user(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    user = await app.services.user_service.get_user_by_username(db, current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
