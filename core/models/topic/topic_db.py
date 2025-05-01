"""话题数据库模型

定义话题的数据库模型和ORM映射，用于话题数据的持久化存储。
所有话题都来自外部抓取，不包含创建话题的功能。
"""

from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from typing import Dict, Any
import time

from core.models.db.session import Base

class Topic(Base):
    """话题数据库模型，用于存储基础话题信息

    提供对话题的数据持久化支持，不包含业务逻辑。
    该模型专注于存储外部抓取的话题数据。
    """
    __tablename__ = "topics"

    id = Column(String(64), primary_key=True, index=True, comment="话题ID")
    title = Column(String(255), nullable=False, comment="话题标题")
    description = Column(Text, nullable=True, comment="话题描述")
    platform = Column(String(50), nullable=True, comment="平台名称")

    # URL相关字段
    url = Column(String(255), nullable=True, comment="话题链接")
    mobile_url = Column(String(255), nullable=True, comment="移动端链接")

    # 内容特性字段
    hot = Column(Integer, default=0, comment="热度值")
    cover = Column(String(255), nullable=True, comment="封面图片URL")

    # 时间相关字段
    created_at = Column(Integer, default=int(time.time()), comment="创建时间")
    updated_at = Column(Integer, default=int(time.time()), onupdate=int(time.time()), comment="更新时间")
    source_time = Column(Integer, nullable=True, comment="来源时间戳")
    expire_time = Column(Integer, nullable=True, comment="过期时间戳")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 字典数据
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'platform': self.platform,
            'url': self.url,
            'mobile_url': self.mobile_url,
            'hot': self.hot,
            'cover': self.cover,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'source_time': self.source_time,
            'expire_time': self.expire_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """从字典创建模型实例

        Args:
            data: 字典数据

        Returns:
            Topic: 模型实例
        """
        # 设置默认时间戳，如果未提供
        current_time = int(time.time())
        if 'source_time' not in data or data['source_time'] is None:
            data['source_time'] = current_time
        if 'expire_time' not in data or data['expire_time'] is None:
            data['expire_time'] = current_time + 7 * 24 * 60 * 60

        return cls(
            id=data.get('id'),
            title=data.get('title'),
            description=data.get('description', ''),
            platform=data.get('platform', ''),
            url=data.get('url', ''),
            mobile_url=data.get('mobile_url', ''),
            hot=data.get('hot', 0),
            cover=data.get('cover', ''),
            created_at=data.get('created_at', current_time),
            updated_at=data.get('updated_at', current_time),
            source_time=data.get('source_time'),
            expire_time=data.get('expire_time'),
        )
