import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Table, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY

from backend.src.models.base import Base


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


# 文章与标签的多对多关系表
article_tag = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", UUID(as_uuid=True), ForeignKey("article.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_name", String(50), ForeignKey("tag.name", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)


class Tag(Base):
    __tablename__ = "tag"

    name = Column(String(50), primary_key=True, index=True, unique=True)
    articles = relationship("backend.src.models.article.Article", secondary=article_tag, back_populates="tags")
    created_at = Column(DateTime, default=datetime.utcnow)


class Article(Base):
    __tablename__ = "article"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(200), nullable=True)
    cover_image = Column(String(255), nullable=True)

    status = Column(String(20), default=ArticleStatus.DRAFT.value, index=True)

    author_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    author = relationship("backend.src.models.user.User", back_populates="articles")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    view_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False, index=True)

    tags = relationship("backend.src.models.article.Tag", secondary=article_tag, back_populates="articles")

    def __repr__(self):
        return f"<Article {self.title}>"
