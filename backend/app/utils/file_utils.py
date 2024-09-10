ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg"}


def is_allowed_file(filename: str) -> bool:
    """
    Memeriksa apakah ekstensi file diizinkan.

    Args:
        filename (str): Nama file yang akan diperiksa.

    Returns:
        bool: True jika file diizinkan, False jika tidak.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
