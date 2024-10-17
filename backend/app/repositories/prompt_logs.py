import logging
from sqlalchemy.orm import Session
from app.models.models import PromptLogs

logger = logging.getLogger(__name__)

class PromptLogsManager:
    def add_prompt_logs(self, db: Session, user_id: int, message: str, system_message: str):
        prompt_logs = PromptLogs(
            user_id=user_id,
            message=message,
            system_message=system_message,
        )
        db.add(prompt_logs)
        db.commit()
        db.refresh(prompt_logs)
        return prompt_logs

prompt_logs_manager = PromptLogsManager()