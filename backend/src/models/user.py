import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.models.base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # admin/user
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String, nullable=True)

    # 关系
    articles = relationship("backend.src.models.article.Article", back_populates="author")

    def __repr__(self):
        return f"<User {self.email}>"
