from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any
from datetime import datetime
import time

from core.db.session import Base
from core.db.utils import JSONEncodedDict
from core.db.model_manager import content_type_style

class ContentType(Base):
    """内容类型模型"""
    __tablename__ = "content_type"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    default_word_count = Column(String(50), nullable=True)
    is_enabled = Column(Boolean, default=True)

    # 模板配置
    prompt_template = Column(Text, nullable=True)
    output_format = Column(JSONEncodedDict, nullable=True)

    # 所需的文章元素
    required_elements = Column(JSONEncodedDict, nullable=True)
    optional_elements = Column(JSONEncodedDict, nullable=True)

    # 与文章风格的多对多关系
    compatible_styles = relationship("ArticleStyle", secondary=content_type_style,
                                    back_populates="compatible_content_types")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ContentType {self.id}:{self.name}>"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "default_word_count": self.default_word_count,
            "is_enabled": self.is_enabled,
            "prompt_template": self.prompt_template,
            "output_format": self.output_format,
            "required_elements": self.required_elements,
            "optional_elements": self.optional_elements,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def is_compatible_with_style(self, style_id: str) -> bool:
        """检查是否与指定风格兼容

        Args:
            style_id: 风格ID

        Returns:
            bool: 是否兼容
        """
        for style in self.compatible_styles:
            if style.id == style_id:
                return True
        return False
