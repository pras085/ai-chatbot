import os

from dotenv import load_dotenv


class Config:
    load_dotenv()
    """
    Kelas konfigurasi untuk menyimpan pengaturan aplikasi.
    """

    # Direktori untuk menyimpan file yang diunggah
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    # Direktori untuk menyimpan file knowledge
    IMAGE_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "knowledge_base_images")

    # Batas maksimum ukuran konten (5 MB)
    MAX_CONTENT_LENGTH = os.getenv("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)

    # API key untuk Claude AI (ambil dari variabel lingkungan)
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

    # Nama model terbaru yang digunakan
    MODEL_NAME = "claude-3-5-sonnet-20240620"

    SECRET_KEY = os.getenv("SECRET_KEY")

    ALGORITHM = os.getenv("ALGORITHM")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
