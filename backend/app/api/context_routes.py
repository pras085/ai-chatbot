import logging
from uuid import UUID

from fastapi import Form, UploadFile, File, Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from app.models.models import User
from app.repositories.database import get_db
from app.repositories.knowledge_base import knowledge_manager
from app.services.auth_service import verify_token
from app.services.user_service import get_user_by_username
from app.utils.file_utils import save_uploaded_file

logger = logging.getLogger(__name__)

context_routes = APIRouter()

@context_routes.post("/context")
async def upload_context(
    text: str = Form(None),
    file: UploadFile = File(None),
    current_user: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        user = await get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if text:
            context = knowledge_manager.add_context(db, user.id, text, "text")
        elif file:
            file_path = await save_uploaded_file(file)
            context = knowledge_manager.add_context(
                db, user.id, file.filename, "file", file_path
            )
        else:
            raise HTTPException(
                status_code=400, detail="Either text or file must be provided"
            )

        return {
            "message": "Context uploaded successfully",
            "context_id": str(context.id),
        }
    except Exception as e:
        logger.error(f"Error uploading context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@context_routes.get("/context")
async def get_context(
    current_user: str = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        user = await get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        context = knowledge_manager.get_latest_context(db, user.id)
        if not context:
            return {"message": "No context found"}
        return {
            "id": str(context.id),
            "content": context.content,
            "content_type": context.content_type,
            "file_path": context.file_path,
            "updated_at": context.updated_at,
        }
    except Exception as e:
        logger.error(f"Error getting context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@context_routes.get("/contexts")
async def get_all_contexts(
    current_user: User = Depends(verify_token), db: Session = Depends(get_db)
):
    try:
        user = await get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        contexts = knowledge_manager.get_user_contexts(db, user.id)
        return [
            {
                "id": str(c.id),
                "content": c.content,
                "content_type": c.content_type,
                "updated_at": c.updated_at,
            }
            for c in contexts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@context_routes.delete("/context/{context_id}")
async def delete_context(
    context_id: UUID,
    current_user: User = Depends(verify_token),
    db: Session = Depends(get_db),
):
    try:
        user = await get_user_by_username(db, current_user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        success = knowledge_manager.delete_context(db, context_id, user.id)
        if success:
            return {"message": "Context deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Context not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
