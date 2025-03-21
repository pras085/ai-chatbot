import os
from fastapi import UploadFile
import logging

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")


def is_allowed_file(filename: str) -> bool:
    """
    Memeriksa apakah ekstensi file diizinkan.

    Args:
        filename (str): Nama file yang akan diperiksa.

    Returns:
        bool: True jika file diizinkan, False jika tidak.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


async def save_uploaded_file(file: UploadFile) -> str:
    """
    Menyimpan file yang diunggah ke direktori uploads.

    Args:
        file (UploadFile): File yang akan disimpan.

    Returns:
        str: Path ke file yang disimpan.

    Raises:
        ValueError: Jika tipe file tidak diizinkan.
    """

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # if not is_allowed_file(file.filename):
    #     raise ValueError("File type not allowed")

    # Tentukan path file
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        logging.info(f"File saved to: {file_path}")
    except Exception as e:
        logging.error(f"Failed to save file {file.filename}. Error: {e}")
        raise
    return file_path
