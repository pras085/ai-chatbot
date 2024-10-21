import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.knowledge_base_manager import KnowledgeManager
from uuid import UUID

logger = logging.getLogger(__name__)
kb = KnowledgeManager()


async def add_knowledge_base_item(
    db: Session, question: str, answer: str
) -> dict:
    try:
        return kb.add_item(db, question, answer)
    except Exception as e:
        logger.error(f"Error adding knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while adding knowledge base item",
        )


async def update_knowledge_base_item(
    db: Session, item_id: UUID, question: str, answer: str
) -> dict:
    try:
        return kb.update_item(db, item_id, question, answer)
    except Exception as e:
        logger.error(f"Error updating knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating knowledge base item",
        )


async def delete_knowledge_base_item(db: Session, item_id: UUID) -> bool:
    try:
        return kb.delete_item(db, item_id)
    except Exception as e:
        logger.error(f"Error deleting knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while deleting knowledge base item",
        )


async def get_all_knowledge_base_items(db: Session) -> list:
    try:
        return kb.get_all_items(db)
    except Exception as e:
        logger.error(f"Error getting all knowledge base items: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting all knowledge base items",
        )


async def get_knowledge_base_item(db: Session, item_id: UUID) -> Optional[dict]:
    try:
        return kb.get_item_by_id(db, item_id)
    except Exception as e:
        logger.error(f"Error getting knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting knowledge base item",
        )
