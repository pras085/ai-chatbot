import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.repositories.code_check_rules_manager import CodeCheckRulesManager
from app.utils.feature_utils import Feature

logger = logging.getLogger(__name__)
code_rules_manager = CodeCheckRulesManager()

async def add_rules(
        db: Session,
        rules: str,
        feature: Feature
):
    return code_rules_manager.add_rules(db, rules, feature)


async def get_rules_by_type(db: Session, feature: Feature) -> Dict[str, Any]:
    return code_rules_manager.get_rules_by_type(db, feature)


async def get_rules(db: Session) -> List[Dict[str, Any]]:
    return code_rules_manager.get_rules(db)


async def update_rules(db: Session, feature: Feature, rules: str) -> bool:
    return code_rules_manager.update_rules(db, feature, rules)


async def delete_rules(db: Session, feature: Feature) -> bool:
    return code_rules_manager.delete_rules(db, feature)