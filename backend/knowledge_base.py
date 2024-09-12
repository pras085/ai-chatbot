import os
import psycopg2
from psycopg2.extras import DictCursor
from typing import Dict, List


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
        """
        Membuat tabel knowledge_base jika belum ada.
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL
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
