import logging
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.code_check_rules import CodeCheckRules
from app.utils.feature_utils import Feature

logger = logging.getLogger(__name__)

class CodeCheckRulesManager:
    @staticmethod
    def add_rules(db: Session,
                  rules: str,
                  feature: Feature
                  ):
        try:
            new_rule = CodeCheckRules(
                feature=feature.name,
                rule=rules
            )
            db.add(new_rule)
            db.commit()
            db.refresh(new_rule)
            return new_rule
        except Exception as e:
            logger.error(f"Error adding code check rule: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_rules(db: Session) -> List[Dict[str, Any]]:
        try:
            rules = db.query(CodeCheckRules).all()
            return [rule.__dict__ for rule in rules]
        except Exception as e:
            logger.error(f"Error retrieving code check rules: {str(e)}")
            raise

    @staticmethod
    def get_rules_by_type(db: Session, feature: Feature) -> Dict[str, Any]:
        try:
            rule = db.query(CodeCheckRules).filter(CodeCheckRules.feature == feature.name).first()
            return rule.__dict__
        except Exception as e:
            logger.error(f"Error retrieving code check rules: {str(e)}")
            raise

    @staticmethod
    def delete_rules(db: Session, feature: Feature) -> bool:
        try:
            db.query(CodeCheckRules).filter(CodeCheckRules.feature == feature.name).delete()
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting code check rules: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def update_rules(db: Session, feature: Feature, rules: str) -> bool:
        try:
            db.query(CodeCheckRules).filter(CodeCheckRules.feature == feature.name).update({CodeCheckRules.rule: rules})
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating code check rules: {str(e)}")
            db.rollback()
            raise