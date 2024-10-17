import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import User, Chat, Message, ChatFile
from uuid import UUID
from fastapi import HTTPException
import traceback
from sqlalchemy import select
import os

from app.utils.feature_utils import Feature

logger = logging.getLogger(__name__)


class ChatManager:
    def get_user(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, username: str, hashed_password: str) -> User:
        db_user = User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_chat(self, db: Session, user_id: int, feature: Feature = Feature.GENERAL) -> Chat:
        db_chat = Chat(user_id=user_id, title="New Chat", feature=feature.name)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat

    def add_message(
        self,
        db: Session,
        chat_id: UUID,
        content: str,
        is_user: bool,
        file_id: Optional[UUID] = None,
    ) -> Message:
        db_message = Message(
            chat_id=chat_id, content=content, is_user=is_user, file_id=file_id
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_chat_messages(self, db: Session, chat_id: UUID) -> List[Dict[str, Any]]:
        try:
            query = (
                select(Message, ChatFile)
                .outerjoin(ChatFile, Message.file_id == ChatFile.id)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.asc())
            )
            logger.info(f"query:{query}")

            result = db.execute(query).fetchall()

            messages = []
            for message, chat_file in result:
                msg_dict = message.__dict__
                if chat_file:
                    msg_dict["file_name"] = chat_file.file_name
                    msg_dict["file_path"] = chat_file.file_path
                    msg_dict["file_url"] = (
                        f"/uploads/{os.path.basename(chat_file.file_path)}"
                    )
                messages.append(msg_dict)

            logger.info(f"Retrieved {len(messages)} messages for chat {chat_id}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving chat messages: {str(e)}", exc_info=True)
            raise  # Re-raise the exception instead of returning an empty list

    def get_user_chats(self, db: Session, user_id: int) -> List[Chat]:
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(desc(Chat.created_at))
            .all()
        )

    def delete_chat(self, db: Session, chat_id: UUID, user_id: int) -> bool:
        """
        Menghapus chat berdasarkan ID.
        Args:
            db (Session): Sesi repositories SQLAlchemy.
            chat_id (UUID): ID chat yang akan dihapus.

        Returns:
            bool: True jika berhasil dihapus, False jika tidak.

        Raises:
            HTTPException: Jika chat tidak ditemukan atau terjadi kesalahan server.
        """
        try:
            chat = (
                db.query(Chat)
                .filter(Chat.id == chat_id, Chat.user_id == user_id)
                .first()
            )
            logger.info(f"{chat}")
            if not chat:
                return False
            db.query(Message).filter(Message.chat_id == chat_id).delete(
                synchronize_session="fetch"
            )

            db.delete(chat)
            db.commit()
            logger.info(f"Chat with id {chat_id} successfully deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {str(e)}")
            logger.error(traceback.format_exc())  # Ini akan mencetak traceback ke log
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Internal server error while deleting chat"
            )
            return False

    def update_chat_title(self, db: Session, chat_id: UUID, title: str) -> bool:
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.title = title
            db.commit()
            return True
        return False

    def get_latest_chat_id(self, db: Session, user_id: int) -> Optional[UUID]:
        latest_chat = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(desc(Chat.created_at))
            .first()
        )
        return latest_chat.id if latest_chat else None

    def add_file_to_chat(
        self, db: Session, chat_id: UUID, file_name: str, file_path: str
    ) -> UUID:
        try:
            chat_file = ChatFile(
                chat_id=chat_id, file_name=file_name, file_path=file_path
            )
            db.add(chat_file)
            db.commit()
            db.refresh(chat_file)
            logger.info(f"File added to chat {chat_id}: {file_name}")
            return chat_file.id
        except Exception as e:
            logger.error(f"Error adding file to chat: {str(e)}", exc_info=True)
            raise
