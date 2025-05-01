"""进度数据库模型"""


from sqlalchemy import Column, String, DateTime, Text, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from core.models.db.session import Base


class ProgressDB(Base):
    __tablename__ = 'progress'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(String, index=True, nullable=False)  # e.g., article_id
    operation_type = Column(String, nullable=False, index=True) # e.g., 'article_production'
    current_stage = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending", index=True) # e.g., pending, in_progress, completed, failed, paused
    progress_data = Column(JSON, nullable=True) # Store detailed stage info, percentage, etc.
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    error_details = Column(Text, nullable=True) # Store last or critical error messages

    def __repr__(self):
        return f"<ProgressDB(id={self.id}, entity_id='{self.entity_id}', type='{self.operation_type}', status='{self.status}')>"

