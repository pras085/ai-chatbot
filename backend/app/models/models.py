from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    content = Column(String)
    is_user = Column(Boolean)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    chat = relationship("Chat", back_populates="messages")
    file = relationship("ChatFile", back_populates="message", uselist=False)


class ChatFile(Base):
    __tablename__ = "chat_files"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"))
    file_name = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    message = relationship("Message", back_populates="file")
