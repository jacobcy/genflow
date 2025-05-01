# core/models/article/article_db.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.models.db.session import Base
from core.models.db.association_tables import article_category_association, article_topic_association


class ArticleDB(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    status = Column(String, default='draft', index=True)
    # 使用 meta_data 替代 metadata
    meta_data = Column(JSON)  # Store additional metadata like source URL, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))

    # Relationships
    author_id = Column(Integer, ForeignKey('users.id'))  # Assuming a User model exists
    author = relationship("User", back_populates="articledbs") # Renamed from articles

    # Many-to-Many with Category
    categories = relationship("Category", secondary=article_category_association, back_populates="articledbs") # Renamed from articles

    # Many-to-Many with Topic
    topics = relationship("Topic", secondary=article_topic_association, back_populates="articledbs") # Renamed from articles

    # One-to-Many with Publication (assuming Publication model tracks publishing events)
    publications = relationship("Publication", back_populates="articledb") # Renamed from article

    # Relationship to ArticleStyle (Many-to-One)
    style_id = Column(Integer, ForeignKey('article_style.id'))
    style = relationship("ArticleStyle", back_populates="articledbs") # Renamed from articles

    # Relationship to ContentType (Many-to-One)
    content_type_id = Column(Integer, ForeignKey('content_type.id'))
    content_type = relationship("ContentType", back_populates="articledbs") # Renamed from articles

    def __repr__(self):
        return f"<ArticleDB(id={self.id}, title='{self.title[:20]}...', status='{self.status}')>"


# You might need a User model if it doesn't exist
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     # ... other user fields
#     articles = relationship("Article", back_populates="author")

# Publication model example (adjust as needed)
# class Publication(Base):
#     __tablename__ = 'publications'
#     id = Column(Integer, primary_key=True)
#     article_id = Column(Integer, ForeignKey('articles.id'))
#     platform_id = Column(Integer, ForeignKey('platforms.id')) # Assuming Platform model
#     published_at = Column(DateTime(timezone=True), server_default=func.now())
#     status = Column(String) # e.g., 'success', 'failed'
#     details = Column(Text) # e.g., URL of published content
#
#     article = relationship("Article", back_populates="publications")
#     platform = relationship("Platform") # Assuming Platform model
