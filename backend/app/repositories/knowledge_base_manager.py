import logging
from typing import List, Dict, Any

from sqlalchemy import or_
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.models import KnowledgeBase

logger = logging.getLogger(__name__)


class KnowledgeManager:
    @staticmethod
    def get_all_items(db: Session) -> List[Dict[str, Any]]:
        try:
            items = db.query(KnowledgeBase).all()
            return [item.__dict__ for item in items]
        except Exception as e:
            logger.error(f"Error retrieving all product knowledge items: {str(e)}")
            raise

    @staticmethod
    def add_item(db: Session, question: str, answer: str) -> Dict[str, Any]:
        try:
            new_item = KnowledgeBase(question=question, answer=answer)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return new_item.__dict__
        except Exception as e:
            logger.error(f"Error adding product knowledge item: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def update_item(db: Session, item_id: UUID, question: str, answer: str) -> Dict[str, Any]:
        try:
            item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
            if item:
                item.question = question
                item.answer = answer
                db.commit()
                db.refresh(item)
                return item.__dict__
            else:
                raise ValueError(f"Item with ID {item_id} not found")
        except Exception as e:
            logger.error(f"Error updating product knowledge item: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def delete_item(db: Session, item_id: UUID) -> bool:
        try:
            item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
            if item:
                db.delete(item)
                db.commit()
                return True
            else:
                raise ValueError(f"Item with ID {item_id} not found")
        except Exception as e:
            logger.error(f"Error deleting product knowledge item: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def search_items(db: Session, query: str) -> List[Dict[str, Any]]:
        try:
            items = (
                db.query(KnowledgeBase)
                .filter(
                    or_(
                        KnowledgeBase.question.ilike(f"%{query}%"),
                        KnowledgeBase.answer.ilike(f"%{query}%"),
                    )
                )
                .all()
            )
            return [item.__dict__ for item in items]
        except Exception as e:
            logger.error(f"Error searching product knowledge items: {str(e)}")
            raise


    @staticmethod
    def get_item_by_id(db: Session, item_id: UUID) -> Dict[str, Any]:
        try:
            item = db.query(KnowledgeBase).filter(KnowledgeBase.id == item_id).first()
            if item:
                return item.__dict__
            else:
                raise ValueError(f"Item with ID {item_id} not found")
        except Exception as e:
            logger.error(f"Error getting product knowledge item: {str(e)}")
            raise


knowledge_manager = KnowledgeManager()
