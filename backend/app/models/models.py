from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid
from app.database import Base


class BaseModel(Base):
    __abstract__ = True

    def to_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

    contexts = relationship("Context", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="chats")
    messages = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan"
    )
    files = relationship(
        "ChatFile", back_populates="chat", cascade="all, delete-orphan"
    )
    __table_args__ = (
        Index("idx_chats_user_id", "user_id"),
        Index("idx_chats_created_at", "created_at"),
    )


class Message(Base):
    __tablename__ = "messages"
    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    chat_id = Column(pgUUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    file_id = Column(pgUUID(as_uuid=True), ForeignKey("chat_files.id"), nullable=True)
    chat = relationship("Chat", back_populates="messages")
    file = relationship("ChatFile", back_populates="messages")


class ChatFile(Base):
    __tablename__ = "chat_files"
    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    chat_id = Column(pgUUID(as_uuid=True), ForeignKey("chats.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    chat = relationship("Chat", back_populates="files")
    messages = relationship("Message", back_populates="file")
    __table_args__ = (
        Index("idx_chat_files_chat_id", "chat_id"),
        Index("idx_chat_files_uploaded_at", "uploaded_at"),
    )


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    def __repr__(self):
        return f"<KnowledgeBase(id={self.id}, question={self.question[:30]}...)>"


class Context(Base):
    __tablename__ = "contexts"

    id = Column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    content_type = Column(String, nullable=False)  # 'text' atau 'file'
    file_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="contexts")


User.contexts = relationship(
    "Context", order_by=Context.created_at, back_populates="user"
)
