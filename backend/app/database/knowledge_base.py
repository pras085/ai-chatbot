from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import KnowledgeBase
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class KnowledgeManager:
    def get_all_items(self, db: Session) -> List[Dict[str, Any]]:
        try:
            items = db.query(KnowledgeBase).all()
            return [item.__dict__ for item in items]
        except Exception as e:
            logger.error(f"Error retrieving all product knowledge items: {str(e)}")
            raise

    def add_item(self, db: Session, question: str, answer: str) -> Dict[str, Any]:
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

    def search_items(self, db: Session, query: str) -> List[Dict[str, Any]]:
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


knowledge_manager = KnowledgeManager()
