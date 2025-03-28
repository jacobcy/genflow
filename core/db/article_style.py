from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any
from datetime import datetime
import time

from core.db.session import Base
from core.db.utils import JSONEncodedDict
from core.db.model_manager import content_type_style

class ArticleStyle(Base):
    """文章风格模型"""

    __tablename__ = "article_style"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 风格特性
    tone = Column(String(100), nullable=True)
    style_characteristics = Column(JSONEncodedDict, nullable=True)
    language_preference = Column(JSONEncodedDict, nullable=True)
    writing_format = Column(JSONEncodedDict, nullable=True)

    # 模板配置
    prompt_template = Column(Text, nullable=True)
    example = Column(Text, nullable=True)

    # 与内容类型的多对多关系
    compatible_content_types = relationship("ContentType", secondary=content_type_style,
                                         back_populates="compatible_styles")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ArticleStyle {self.id}:{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_enabled": self.is_enabled,
            "tone": self.tone,
            "style_characteristics": self.style_characteristics,
            "language_preference": self.language_preference,
            "writing_format": self.writing_format,
            "prompt_template": self.prompt_template,
            "example": self.example,
            "content_types": [ct.id for ct in self.compatible_content_types],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_compatible_with_content_type(self, content_type_id: str) -> bool:
        """检查是否与指定内容类型兼容

        Args:
            content_type_id: 内容类型ID

        Returns:
            bool: 是否兼容
        """
        for ct in self.compatible_content_types:
            if ct.id == content_type_id:
                return True
        return False
