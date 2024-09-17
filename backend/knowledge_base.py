import os
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List, Any
import logging


class KnowledgeBase:
    """
    Kelas untuk mengelola interaksi dengan database PostgreSQL yang menyimpan knowledge base.
    """

    def __init__(self):
        """
        Inisialisasi koneksi database dan memastikan tabel yang diperlukan ada.
        """
        self.conn_params = {
            "dbname": os.getenv("DB_NAME", "muatmuat_db"),
            "user": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
        }
        self._create_table()

    def _create_table(self):
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL
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

    def add_item(self, question: str, answer: str):
        """
        Menambahkan item baru ke knowledge base.

        Args:
            question (str): Pertanyaan untuk ditambahkan.
            answer (str): Jawaban yang sesuai dengan pertanyaan.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO knowledge_base (question, answer) VALUES (%s, %s)",
                    (question, answer),
                )
            conn.commit()

    def get_all_items(self) -> List[Dict[str, str]]:
        """
        Mengambil semua item dari knowledge base.

        Returns:
            List[Dict[str, str]]: Daftar dictionary yang berisi pasangan pertanyaan dan jawaban.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT question, answer FROM knowledge_base")
                return [dict(row) for row in cur.fetchall()]

    def search_items(self, query: str) -> List[Dict[str, str]]:
        """
        Mencari item dalam knowledge base berdasarkan query.

        Args:
            query (str): String pencarian.

        Returns:
            List[Dict[str, str]]: Daftar dictionary yang berisi pasangan pertanyaan dan jawaban yang cocok dengan query.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "SELECT question, answer FROM knowledge_base WHERE question ILIKE %s OR answer ILIKE %s",
                    (f"%{query}%", f"%{query}%"),
                )
                return [dict(row) for row in cur.fetchall()]

    def create_chat(self, user_id: str) -> int:
        """
        Membuat chat baru dan mengembalikan ID-nya.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chats (user_id) VALUES (%s) RETURNING id", (user_id,)
                )
                chat_id = cur.fetchone()[0]
            conn.commit()
        return chat_id

    def add_message(self, chat_id: int, content: str, is_user: bool):
        """
        Menambahkan pesan ke chat tertentu.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO messages (chat_id, content, is_user) VALUES (%s, %s, %s)",
                    (chat_id, content, is_user),
                )
            conn.commit()

    def get_chat_messages(self, chat_id: int) -> List[Dict[str, Any]]:
        """
        Mengambil semua pesan untuk chat tertentu.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "SELECT id, chat_id, content, is_user, timestamp FROM messages WHERE chat_id = %s ORDER BY timestamp",
                    (chat_id,),
                )
                results = [dict(row) for row in cur.fetchall()]
                logging.info(f"Retrieved {len(results)} messages")
                return results

    def get_user_chats(self, user_id: str):
        """
        Mengambil semua chat untuk user tertentu.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "SELECT * FROM chats WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,),
                )
                return cur.fetchall()

    def create_new_chat(self, user_id: str):
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chats (user_id) VALUES (%s) RETURNING id", (user_id,)
                )
                chat_id = cur.fetchone()[0]
            conn.commit()
        return {"id": chat_id, "user_id": user_id}

    def update_chat_title(self, chat_id: int, title: str):
        """
        Mengupdate judul chat.

        Args:
            chat_id (int): ID chat yang akan diupdate.
            title (str): Judul baru untuk chat.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE chats SET title = %s WHERE id = %s", (title, chat_id)
                )
            conn.commit()

    def get_latest_chat_id(self, user_id: str) -> int:
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(id) FROM chats WHERE user_id = %s", (user_id,))
                result = cur.fetchone()
        return result[0] if result else None

    def add_file_to_chat(self, chat_id: int, file_name: str, file_path: str):
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chat_files (chat_id, file_name, file_path) VALUES (%s, %s, %s)",
                    (chat_id, file_name, file_path),
                )
            conn.commit()
