from uuid import UUID
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from ..db.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(PGUUID, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # admin/user
    hashed_password = Column(String, nullable=False)
    is_active = Column(String, default=True)
    
    def __repr__(self):
        return f"<User {self.email}>" 