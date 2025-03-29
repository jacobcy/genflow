"""内容类型名称引用的数据库模型，用于与其他表进行关联
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from typing import Dict, Any, List
from datetime import datetime

from core.models.db.session import Base
from core.models.content_type.constants import (
    CONTENT_TYPE_FLASH_NEWS, CONTENT_TYPE_SOCIAL_MEDIA, CONTENT_TYPE_NEWS,
    CONTENT_TYPE_BLOG, CONTENT_TYPE_TUTORIAL
)

class ContentTypeName(Base):
    """内容类型名称引用，仅用于数据库关联"""
    __tablename__ = "content_type_name"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    name = Column(String(100), primary_key=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ContentTypeName {self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        # 处理SQLAlchemy对象的属性访问
        created_at_value = None
        if hasattr(self, 'created_at') and self.created_at is not None:
            if isinstance(self.created_at, datetime):
                created_at_value = self.created_at.isoformat()

        return {
            "name": self.name,
            "created_at": created_at_value
        }

# 预定义的内容类型名称
DEFAULT_CONTENT_TYPES = [
    CONTENT_TYPE_FLASH_NEWS,
    CONTENT_TYPE_SOCIAL_MEDIA,
    CONTENT_TYPE_NEWS,
    CONTENT_TYPE_BLOG,
    CONTENT_TYPE_TUTORIAL
]

def ensure_default_content_types(session) -> None:
    """确保默认内容类型名称存在于数据库中

    Args:
        session: 数据库会话
    """
    for type_name in DEFAULT_CONTENT_TYPES:
        # 检查是否已存在
        existing = session.query(ContentTypeName).filter(ContentTypeName.name == type_name).first()
        if not existing:
            # 如果不存在，则创建
            content_type = ContentTypeName(name=type_name)
            session.add(content_type)

    # 提交事务
    session.commit()
