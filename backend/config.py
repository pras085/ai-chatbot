import os
import psycopg2


class Config:
    """
    Kelas konfigurasi untuk menyimpan pengaturan aplikasi.
    """

    # Direktori untuk menyimpan file yang diunggah
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    # Batas maksimum ukuran konten (5 MB)
    MAX_CONTENT_LENGTH = os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)

    # API key untuk Claude AI (ambil dari variabel lingkungan)
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    # Nama model terbaru yang digunakan
    MODEL_NAME = "claude-3-5-sonnet-20240620"


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "muatmuat_db"),
        user=os.getenv("DB_USER", ""),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
