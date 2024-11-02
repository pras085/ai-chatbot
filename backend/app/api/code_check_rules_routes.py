import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.code_check_rules import CreateCheckRules, UpdateCheckRules
from app.models.jwt import JwtUser
from app.services import code_check_rules_service
from app.services.auth_service import verify_token
from app.utils.feature_utils import Feature

code_check_rules_routes = APIRouter()
logger = logging.getLogger(__name__)


@code_check_rules_routes.get("/code-check-rules")
async def get_code_check_rules(
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.get_rules(db)


@code_check_rules_routes.post("/code-check-rules")
async def add_code_check_rules(
    req_body: CreateCheckRules,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.add_rules(db, req_body.rule, req_body.feature)

@code_check_rules_routes.get("/code-check-rules/{feature}")
async def get_code_check_rules_by_feature(
    feature: Feature,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.get_rules_by_type(db, feature)

@code_check_rules_routes.delete("/code-check-rules/{feature}")
async def delete_code_check_rules(
    feature: Feature,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.delete_rules(db, feature)


@code_check_rules_routes.put("/code-check-rules/{feature}")
async def update_code_check_rules(
    feature: Feature,
    req_body: UpdateCheckRules,
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.update_rules(db, feature, req_body.rule)

@code_check_rules_routes.get("/code-check-rules/x/init")
async def init_code_check_rules(
    current_user: JwtUser = Depends(verify_token),
    db: Session = Depends(get_db)
):
    return await code_check_rules_service.init_rules(db)
