from typing import Optional

from sqlalchemy.orm import Session

from app.models.models import User


class UserManager:
    def get_user(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create_user(self, db: Session, username: str, hashed_password: str) -> User:
        db_user = User(username=username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

