import logging
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.models import Context

logger = logging.getLogger(__name__)

class ContextManager:
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


context_manager = ContextManager()