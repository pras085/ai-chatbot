import logging
from typing import Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.repositories.knowledge_base_manager import KnowledgeManager
from app.utils.file_utils import save_uploaded_file

logger = logging.getLogger(__name__)
kb = KnowledgeManager()


async def add_knowledge_base_item(
    db: Session, question: str, answer: str, image: Optional[UploadFile] = None
) -> dict:
    """
    Menambahkan item baru ke knowledge base.

    Args:
        db (Session): Sesi repositories SQLAlchemy.
        question (str): Pertanyaan untuk item knowledge base.
        answer (str): Jawaban untuk item knowledge base.
        image (Optional[UploadFile]): File gambar yang diunggah, jika ada.

    Returns:
        dict: Informasi tentang item knowledge base yang baru ditambahkan.

    Raises:
        HTTPException: Jika terjadi kesalahan server internal saat menambahkan item ke knowledge base.
    """
    try:
        image_path = None
        if image:
            image_path = await save_uploaded_file(image)

        return kb.add_item(db, question, answer, image_path)
    except Exception as e:
        logger.error(f"Error adding knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while adding knowledge base item",
        )
