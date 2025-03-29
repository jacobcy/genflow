from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any, List
from datetime import datetime
import time

from core.models.db.session import Base
from core.models.db.utils import JSONEncodedDict
from core.models.db.model_manager import content_type_style

class ArticleStyle(Base):
    """文章风格模型"""

    __tablename__ = "article_style"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    name = Column(String(100), primary_key=True, index=True, nullable=False)
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

    # 与内容类型名称的多对多关系
    compatible_content_types = relationship(
        "content_type_style",
        primaryjoin="ArticleStyle.name == content_type_style.c.style_name",
        viewonly=True
    )

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ArticleStyle {self.name}>"

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
            "tone": self.tone,
            "style_characteristics": self.style_characteristics,
            "language_preference": self.language_preference,
            "writing_format": self.writing_format,
            "prompt_template": self.prompt_template,
            "example": self.example,
            "content_types": [rel.content_type_name for rel in self.compatible_content_types],
            "created_at": created_at_value,
            "updated_at": updated_at_value
        }

    def is_compatible_with_content_type(self, content_type_name: str) -> bool:
        """检查是否与指定内容类型兼容

        Args:
            content_type_name: 内容类型名称

        Returns:
            bool: 是否兼容
        """
        for rel in self.compatible_content_types:
            if rel.content_type_name == content_type_name:
                return True
        return False

    def get_compatible_content_types(self) -> List[str]:
        """获取兼容的内容类型名称列表

        Returns:
            List[str]: 内容类型名称列表
        """
        return [rel.content_type_name for rel in self.compatible_content_types]
