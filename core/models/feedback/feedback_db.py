"""反馈数据库模型

定义反馈相关的数据库模型，用于持久化存储反馈信息。
"""
from sqlalchemy import Column, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from ..db.session import Base

class FeedbackDB(Base):
    """反馈数据库模型基类"""
    __tablename__ = "feedback"

    id = Column(UUID, primary_key=True, default=uuid4)
    feedback_type = Column(String, nullable=False)  # 'research' 或 'content'
    feedback_text = Column(String, nullable=False)
    rating = Column(Float, nullable=True)  # 通用评分字段
    feedback_source = Column(String, default="system")  # 'system' 或 'human'
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 通用元数据字段，存储不同类型反馈的特定数据
    feedback_metadata = Column(JSON, default=dict)

    __mapper_args__ = {
        'polymorphic_on': feedback_type,
        'polymorphic_identity': 'feedback'
    }

class ResearchFeedbackDB(FeedbackDB):
    """研究反馈数据库模型"""
    __mapper_args__ = {
        'polymorphic_identity': 'research'
    }

    accuracy_rating = Column(Float, nullable=True)
    completeness_rating = Column(Float, nullable=True)
    research_id = Column(String, nullable=True)  # 关联的研究ID

class ContentFeedbackDB(FeedbackDB):
    """内容反馈数据库模型"""
    __mapper_args__ = {
        'polymorphic_identity': 'content'
    }

    content_id = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
