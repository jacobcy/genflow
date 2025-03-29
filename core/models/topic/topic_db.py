from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from typing import Dict, Any
import time

from core.models.db.session import Base

class Topic(Base):
    """话题模型，用于存储基础话题信息

    提供对话题的数据持久化支持，不包含业务逻辑
    """
    __tablename__ = "topics"

    id = Column(String(64), primary_key=True, index=True, comment="话题ID")
    title = Column(String(255), nullable=False, comment="话题标题")
    description = Column(Text, nullable=True, comment="话题描述")
    content_type = Column(String(50), nullable=True, comment="内容类型")
    platform = Column(String(50), nullable=True, comment="平台名称")
    url = Column(String(255), nullable=True, comment="话题链接")
    keywords = Column(Text, nullable=True, comment="关键词，以逗号分隔")
    language = Column(String(10), default="zh-CN", comment="语言")

    created_at = Column(Integer, default=int(time.time()), comment="创建时间")
    updated_at = Column(Integer, default=int(time.time()), onupdate=int(time.time()), comment="更新时间")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 字典数据
        """
        keywords_list = []
        if self.keywords and isinstance(self.keywords, str):
            keywords_list = [k.strip() for k in self.keywords.split(",")]

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'platform': self.platform,
            'url': self.url,
            'keywords': keywords_list,
            'language': self.language,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """从字典创建模型

        Args:
            data: 字典数据

        Returns:
            Topic: 模型实例
        """
        # 处理keywords字段
        keywords = data.get('keywords', [])
        if isinstance(keywords, list):
            keywords = ",".join(keywords)

        return cls(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description', ''),
            content_type=data.get('content_type'),
            platform=data.get('platform', ''),
            url=data.get('url', ''),
            keywords=keywords,
            language=data.get('language', 'zh-CN'),
            created_at=data.get('created_at', int(time.time())),
            updated_at=data.get('updated_at', int(time.time())),
        )
