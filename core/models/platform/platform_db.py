from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any
from datetime import datetime
import time

from core.models.db.session import Base
from core.models.db.utils import JSONEncodedDict

class Platform(Base):
    """平台配置模型"""
    __tablename__ = "platform"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    name = Column(String(100), primary_key=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 平台特性
    platform_type = Column(String(50), nullable=True)
    url = Column(String(255), nullable=True)
    logo_url = Column(String(255), nullable=True)

    # 平台限制
    max_title_length = Column(JSONEncodedDict, nullable=True)
    max_content_length = Column(JSONEncodedDict, nullable=True)
    allowed_media_types = Column(JSONEncodedDict, nullable=True)

    # API配置
    api_config = Column(JSONEncodedDict, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Platform {self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        # 处理SQLAlchemy对象的属性访问
        created_at_value = None
        updated_at_value = None

        if hasattr(self, 'created_at') and self.created_at is not None:
            if isinstance(self.created_at, datetime):
                created_at_value = self.created_at.isoformat()

        if hasattr(self, 'updated_at') and self.updated_at is not None:
            if isinstance(self.updated_at, datetime):
                updated_at_value = self.updated_at.isoformat()

        return {
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "platform_type": self.platform_type,
            "url": self.url,
            "logo_url": self.logo_url,
            "max_title_length": self.max_title_length,
            "max_content_length": self.max_content_length,
            "allowed_media_types": self.allowed_media_types,
            "api_config": self.api_config,
            "created_at": created_at_value,
            "updated_at": updated_at_value
        }
