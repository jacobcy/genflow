from typing import Optional, Union
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.security import get_password_hash, verify_password
from models.user import User
from schemas.auth import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[User]:
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_in: UserCreate) -> Optional[User]:
        db_user = User(
            id=uuid.uuid4(),
            email=user_in.email,
            name=user_in.name,
            role="user",
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
        )
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except SQLAlchemyError:
            self.db.rollback()
            return None

    def update(self, user: User, user_in: UserUpdate) -> User:
        if user_in.password:
            user.hashed_password = get_password_hash(user_in.password)
        if user_in.name:
            user.name = user_in.name
        if user_in.role:
            user.role = user_in.role
        if user_in.email:
            user.email = user_in.email

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except SQLAlchemyError:
            self.db.rollback()
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active == True

    def is_admin(self, user: User) -> bool:
        return user.role == "admin"
