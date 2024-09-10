import os


class Config:
    """
    Kelas konfigurasi untuk menyimpan pengaturan aplikasi.
    """

    # Direktori untuk menyimpan file yang diunggah
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")

    # Batas maksimum ukuran konten (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # API key untuk Claude AI (ambil dari variabel lingkungan)
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
