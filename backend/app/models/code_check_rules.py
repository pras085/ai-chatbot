import uuid

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, func, Text, String

from app.config.database import Base
from sqlalchemy.dialects.postgresql import UUID

from app.utils.feature_utils import Feature


class CodeCheckRules(Base):
    __tablename__ = "code_check_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    feature = Column(String, nullable=False)
    rule = Column(Text, nullable=False)

class CreateCheckRules(BaseModel):
    feature: Feature = Feature.GENERAL
    rule: str

class UpdateCheckRules(BaseModel):
    rule: str

