from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from ..db.base_class import Base

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(PGUUID, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(PGUUID, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")  # draft/published
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="articles")
    
    def __repr__(self):
        return f"<Article {self.title}>" 