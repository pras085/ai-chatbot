import os
from psycopg2.extras import DictCursor
from typing import Dict, List, Any
import logging
import psycopg2

logger = logging.getLogger(__name__)


class ChatManager:
    def __init__(self):
        """
        Inisialisasi ChatManager dengan parameter koneksi database.
        """
        self.conn_params = {
            "dbname": os.getenv("DB_NAME", "muatmuat_db"),
            "user": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }
        self._create_table()

    def get_connection(self):
        return psycopg2.connect(**self.conn_params)

    def _create_table(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        image_path TEXT
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chats (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        chat_id INTEGER REFERENCES chats(id),
                        content TEXT NOT NULL,
                        is_user BOOLEAN NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_files (
                        id SERIAL PRIMARY KEY,
                        chat_id INTEGER REFERENCES chats(id),
                        file_name TEXT NOT NULL,
                        file_path TEXT NOT NULL,
                        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            conn.commit()

    def create_chat(self, user_id: str) -> int:
        """
        Membuat chat baru untuk pengguna tertentu.

        Args:
            user_id (str): ID pengguna yang membuat chat.

        Returns:
            int: ID chat yang baru dibuat.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chats (user_id) VALUES (%s) RETURNING id", (user_id,)
                )
                chat_id = cur.fetchone()[0]
            conn.commit()
        return chat_id

    def add_message(
        self, chat_id: int, content: str, is_user: bool, file_id: int = None
    ):
        """
        Menambahkan pesan baru ke dalam chat.

        Args:
            chat_id (int): ID chat tempat pesan akan ditambahkan.
            content (str): Isi pesan.
            is_user (bool): True jika pesan dari pengguna, False jika dari sistem.
            file_id (int, optional): ID file yang terkait dengan pesan.

        Returns:
            None
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if file_id is not None:
                        cur.execute(
                            "INSERT INTO messages (chat_id, content, is_user, file_id) VALUES (%s, %s, %s, %s)",
                            (chat_id, content, is_user, file_id),
                        )
                    else:
                        cur.execute(
                            "INSERT INTO messages (chat_id, content, is_user) VALUES (%s, %s, %s)",
                            (chat_id, content, is_user),
                        )
                conn.commit()
            logger.info(f"Added message to chat {chat_id}")
        except Exception as e:
            logger.error(f"Error adding message to chat: {str(e)}", exc_info=True)
            raise

    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Mengambil semua pesan untuk chat tertentu.

        Args:
            chat_id (int): ID chat yang pesannya akan diambil.

        Returns:
            List[Dict[str, Any]]: Daftar pesan dalam format dictionary.
        """

        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(
                        """
                        SELECT m.*, cf.file_name, cf.file_path 
                        FROM messages m
                        LEFT JOIN chat_files cf ON m.file_id = cf.id
                        WHERE m.chat_id = %s 
                        ORDER BY m.timestamp ASC
                        """,
                        (chat_id,),
                    )
                    messages = cur.fetchall()
                    result = []
                    for message in messages:
                        msg_dict = dict(message)
                        if msg_dict["file_name"] and msg_dict["file_path"]:
                            msg_dict["file_url"] = (
                                f"/uploads/{os.path.basename(msg_dict['file_path'])}"
                            )
                        result.append(msg_dict)
                    logger.info(f"Retrieved {len(result)} messages for chat {chat_id}")
                    return result
        except Exception as e:
            logger.error(f"Error retrieving chat messages: {str(e)}", exc_info=True)
            return []

    def get_user_chats(self, user_id: str):
        """
        Mengambil semua chat untuk pengguna tertentu.

        Args:
            user_id (str): ID pengguna.

        Returns:
            List[Dict]: Daftar chat milik pengguna.
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "SELECT * FROM chats WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,),
                )
                return cur.fetchall()

    def delete_new_chat(self, user_id: str):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM chats (user_id) VALUES (%s) RETURNING id", (user_id,)
                )
                chat_id = cur.fetchone()[0]
            conn.commit()
        return {"id": chat_id, "user_id": user_id}

    def create_new_chat(self, user_id: str):
        """
        Membuat chat baru untuk pengguna tertentu.

        Args:
            user_id (str): ID pengguna yang membuat chat.

        Returns:
            Dict: Informasi tentang chat baru yang dibuat.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chats (user_id) VALUES (%s) RETURNING id", (user_id,)
                )
                chat_id = cur.fetchone()[0]
            conn.commit()
        return {"id": chat_id, "user_id": user_id}

    def update_chat_title(self, chat_id: int, title: str):
        """
        Memperbarui judul chat.

        Args:
            chat_id (int): ID chat yang akan diperbarui.
            title (str): Judul baru untuk chat.

        Returns:
            None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE chats SET title = %s WHERE id = %s", (title, chat_id)
                )
            conn.commit()

    def get_latest_chat_id(self, user_id: str) -> int:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(id) FROM chats WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
        return result[0] if result else None

    def add_file_to_chat(self, chat_id: int, file_name: str, file_path: str) -> int:
        """
        Menambahkan informasi file ke database untuk chat tertentu.

        Args:
            chat_id (int): ID chat tempat file ditambahkan.
            file_name (str): Nama file yang diupload.
            file_path (str): Path tempat file disimpan.

        Returns:
            int: ID dari file yang baru ditambahkan.
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO chat_files (chat_id, file_name, file_path) VALUES (%s, %s, %s) RETURNING id",
                        (chat_id, file_name, file_path),
                    )
                    file_id = cur.fetchone()[0]
                conn.commit()
            logger.info(f"File added to chat {chat_id}: {file_name}")
            return file_id
        except Exception as e:
            logger.error(f"Error adding file to chat: {str(e)}", exc_info=True)
            raise
