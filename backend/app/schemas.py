from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


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
    title: str = "New Chat"


class ChatCreate(ChatBase):
    title: Optional[str] = Field(None, description="Chat title")

    class Config:
        extra = "allow"


class Chat(BaseModel):
    id: UUID
    user_id: int
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeBaseBase(BaseModel):
    title: str
    content: str


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBase(KnowledgeBaseBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
