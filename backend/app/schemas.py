from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_orm = True


class ChatBase(BaseModel):
    title: str


class ChatCreate(ChatBase):
    title: Optional[str] = Field(None, description="Chat title")

    class Config:
        extra = "allow"


class Chat(ChatBase):
    id: UUID4
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_orm = True
