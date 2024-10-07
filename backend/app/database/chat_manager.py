import os
import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import User, Chat, Message, ChatFile

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self):
        """
        Inisialisasi ChatManager.
        """
        pass

    def get_user(self, db: Session, username: str) -> User:
        """
        Mengambil data pengguna berdasarkan username.

        Args:
            db (Session): Sesi database SQLAlchemy.
            username (str): Username pengguna yang dicari.

        Returns:
            User: Objek User jika ditemukan, None jika tidak ditemukan.
        """
        user = db.query(User).filter(User.username == username).first()
        logging.info(f"Querying user: {username}, Result: {user}")
        return user

    def create_user(self, db: Session, username: str, hashed_password: str) -> User:
        """
        Membuat pengguna baru.

        Args:
            db (Session): Sesi database SQLAlchemy.
            username (str): Username untuk pengguna baru.
            hashed_password (str): Password yang sudah di-hash.

        Returns:
            User: Objek User yang baru dibuat.
        """
        db_user = User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logging.info(f"Created user: {username}")
        return db_user

    def create_chat(self, db: Session, user_id: int, title: str = "New Chat") -> int:
        """
        Membuat chat baru untuk pengguna tertentu.

        Args:
            db (Session): Sesi database SQLAlchemy.
            user_id (int): ID pengguna yang membuat chat.
            title (str): Judul chat (default: "New Chat").

        Returns:
            int: ID chat yang baru dibuat.
        """
        db_chat = Chat(user_id=user_id, title=title)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
        return db_chat.id

    def add_message(
        self,
        db: Session,
        chat_id: int,
        content: str,
        is_user: bool,
        file_id: int = None,
    ) -> Message:
        """
        Menambahkan pesan baru ke dalam chat.

        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_id (int): ID chat tempat pesan akan ditambahkan.
            content (str): Isi pesan.
            is_user (bool): True jika pesan dari pengguna, False jika dari sistem.
            file_id (int, optional): ID file yang terkait dengan pesan.

        Returns:
            Message: Objek Message yang baru ditambahkan.
        """
        db_message = Message(
            chat_id=chat_id, content=content, is_user=is_user, file_id=file_id
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_chat_messages(self, db: Session, chat_id: int) -> List[Dict[str, Any]]:
        """
        Mengambil semua pesan untuk chat tertentu.

        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_id (int): ID chat yang pesannya akan diambil.

        Returns:
            List[Dict[str, Any]]: Daftar pesan dalam format dictionary.
        """
        try:
            messages = (
                db.query(Message)
                .filter(Message.chat_id == chat_id)
                .order_by(Message.timestamp.asc())
                .all()
            )

            result = []
            for message in messages:
                msg_dict = {
                    "id": message.id,
                    "content": message.content,
                    "is_user": message.is_user,
                    "timestamp": message.timestamp.isoformat(),
                }
                # Tambahkan logika untuk file jika diperlukan
                result.append(msg_dict)

            logger.info(f"Retrieved {len(result)} messages for chat {chat_id}")
            return result
        except Exception as e:
            logger.error(f"Error retrieving chat messages: {str(e)}", exc_info=True)
            return []

    def get_user_chats(self, db: Session, user_id: int) -> List[Chat]:
        """
        Mengambil semua chat untuk pengguna tertentu.

        Args:
            db (Session): Sesi database SQLAlchemy.
            user_id (int): ID pengguna.

        Returns:
            List[Chat]: Daftar objek Chat milik pengguna.
        """
        return (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(desc(Chat.created_at))
            .all()
        )

    def delete_chat(self, db: Session, chat_id: int) -> bool:
        """
        Menghapus chat berdasarkan ID.

        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_id (int): ID chat yang akan dihapus.

        Returns:
            bool: True jika berhasil dihapus, False jika tidak.
        """
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            db.delete(chat)
            db.commit()
            return True
        return False

    def update_chat_title(self, db: Session, chat_id: int, title: str) -> bool:
        """
        Memperbarui judul chat.

        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_id (int): ID chat yang akan diperbarui.
            title (str): Judul baru untuk chat.

        Returns:
            bool: True jika berhasil diperbarui, False jika tidak.
        """
        chat = db.query(Chat).filter(Chat.id == chat_id).first()
        if chat:
            chat.title = title
            db.commit()
            return True
        return False

    def get_latest_chat_id(self, db: Session, user_id: int) -> int:
        """
        Mendapatkan ID chat terbaru untuk pengguna tertentu.

        Args:
            db (Session): Sesi database SQLAlchemy.
            user_id (int): ID pengguna.

        Returns:
            int: ID chat terbaru, atau None jika tidak ada.
        """
        latest_chat = (
            db.query(Chat)
            .filter(Chat.user_id == user_id)
            .order_by(desc(Chat.created_at))
            .first()
        )
        return latest_chat.id if latest_chat else None

    def add_file_to_chat(
        self, db: Session, chat_id: int, file_name: str, file_path: str
    ) -> int:
        """
        Menambahkan informasi file ke database untuk chat tertentu.

        Args:
            db (Session): Sesi database SQLAlchemy.
            chat_id (int): ID chat tempat file ditambahkan.
            file_name (str): Nama file yang diupload.
            file_path (str): Path tempat file disimpan.

        Returns:
            int: ID dari file yang baru ditambahkan.
        """
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
