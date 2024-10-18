from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import KnowledgeBase, Context
from typing import List, Dict, Any, Optional
import logging
import uuid

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

    def add_context(
        self,
        db: Session,
        user_id: int,
        content: str,
        content_type: str,
        content_raw: str = None,
        file_path: str = None,
    ):
        try:
            logger.info(f"Adding context for user {user_id}: {content_type}")
            new_context = Context(
                user_id=user_id,
                content=content,
                content_type=content_type,
                file_path=file_path,
                content_raw=content_raw,
            )
            db.add(new_context)
            db.commit()
            db.refresh(new_context)
            logger.info(f"Context added successfully: {new_context.id}")
            return new_context
        except Exception as e:
            logger.error(f"Error adding context: {str(e)}")
            db.rollback()
            raise

    def get_user_contexts(self, db: Session, user_id: int) -> List[Context]:
        try:
            return (
                db.query(Context)
                .filter(Context.user_id == user_id)
                .order_by(Context.updated_at.desc())
                .all()
            )
        except Exception as e:
            logger.error(f"Error getting user contexts: {str(e)}")
            raise

    def get_latest_context(self, db: Session, user_id: int) -> Optional[List[Context]]:
        try:
            logger.info(f"Getting latest context for user_id: {user_id}")
            context = (
                db.query(Context)
                .filter(Context.user_id == user_id)
                .order_by(Context.updated_at.desc())
                .all()
            )
            if not context:  # Jika tidak ada context
                logger.info(f"No context found for user {user_id}")
                return None  # Atau berikan nilai default sesuai keperluan
            return context
        except Exception as e:
            logger.error(f"Error getting latest context: {str(e)}")
            raise

    def delete_context(self, db: Session, context_id: uuid.UUID, user_id: int) -> bool:
        try:
            context = (
                db.query(Context)
                .filter(Context.id == context_id, Context.user_id == user_id)
                .first()
            )
            if context:
                db.delete(context)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting context: {str(e)}")
            db.rollback()
            raise


knowledge_manager = KnowledgeManager()
