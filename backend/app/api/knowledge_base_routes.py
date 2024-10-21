import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.jwt import JwtUser
from app.services import knowledge_base_service
from app.services.auth_service import verify_token
from uuid import UUID

logger = logging.getLogger(__name__)

knowledge_base_routes = APIRouter()


@knowledge_base_routes.get("/knowledge-base")
async def get_knowledge_base(
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        return await knowledge_base_service.get_all_knowledge_base_items(db)
    except Exception as e:
        logger.error(f"Error getting knowledge base: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while getting knowledge base"
        )


@knowledge_base_routes.get("/knowledge-base/{item_id}")
async def get_knowledge_base_item(
    item_id: UUID,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        return await knowledge_base_service.get_knowledge_base_item(db, item_id)
    except Exception as e:
        logger.error(f"Error getting knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while getting knowledge base item"
        )


@knowledge_base_routes.post("/knowledge-base")
async def add_knowledge_base_item(
    question: str,
    answer: str,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        return await knowledge_base_service.add_knowledge_base_item(db, question, answer)
    except Exception as e:
        logger.error(f"Error adding knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while adding knowledge base item"
        )


@knowledge_base_routes.put("/knowledge-base/{item_id}")
async def update_knowledge_base_item(
    item_id: UUID,
    question: str,
    answer: str,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        return await knowledge_base_service.update_knowledge_base_item(db, item_id, question, answer)
    except Exception as e:
        logger.error(f"Error updating knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while updating knowledge base item"
        )


@knowledge_base_routes.delete("/knowledge-base/{item_id}")
async def delete_knowledge_base_item(
    item_id: UUID,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        return await knowledge_base_service.delete_knowledge_base_item(db, item_id)
    except Exception as e:
        logger.error(f"Error deleting knowledge base item: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while deleting knowledge base item"
        )
