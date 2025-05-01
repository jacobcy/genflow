from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any, List
from datetime import datetime
import time

from core.models.db.session import Base
from core.models.db.utils import JSONEncodedDict
# from .association_tables import content_type_style # Comment out if association_tables.py missing or unused
# from core.models.content_type.content_type_db import ContentTypeName # Comment out if relationship unused

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

    # 与内容类型名称的多对多关系 - Temporarily commented out
    # compatible_content_types = relationship(
    #     "ContentTypeName",
    #     secondary=content_type_style,
    # )

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

        # Get compatible content type names from the related objects
        compatible_names = []
        # if self.compatible_content_types: # Check if relationship is loaded/populated - Commented out
        #      try:
        #          compatible_names = [ct_obj.name for ct_obj in self.compatible_content_types]
        #      except Exception as e:
        #          # Log error if accessing relationship fails unexpectedly
        #          pass # Handle appropriately

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
            # "content_types": compatible_names, # Use names from related ContentTypeName objects - Commented out
            "created_at": created_at_value,
            "updated_at": updated_at_value
        }
