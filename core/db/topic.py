from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any
import time

from core.db.session import Base
from core.db.utils import JSONEncodedDict

class Topic(Base):
    """话题模型"""
    __tablename__ = "topics"

    id = Column(String(64), primary_key=True, index=True, comment="话题ID")
    title = Column(String(255), nullable=False, comment="话题标题")
    platform = Column(String(50), nullable=False, comment="平台名称")
    description = Column(Text, nullable=True, comment="话题描述")
    url = Column(String(255), nullable=True, comment="话题链接")
    mobile_url = Column(String(255), nullable=True, comment="移动端链接")
    cover = Column(String(255), nullable=True, comment="封面图片")
    hot = Column(Integer, default=0, comment="热度值")
    trend_score = Column(Float, default=0.0, comment="趋势得分")
    source_time = Column(Integer, default=int(time.time()), comment="数据源时间")
    expire_time = Column(Integer, default=lambda: int(time.time()) + 7 * 24 * 60 * 60, comment="过期时间")

    created_at = Column(Integer, default=int(time.time()), comment="创建时间")
    updated_at = Column(Integer, default=int(time.time()), onupdate=int(time.time()), comment="更新时间")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 字典数据
        """
        return {
            'id': self.id,
            'title': self.title,
            'platform': self.platform,
            'description': self.description,
            'url': self.url,
            'mobile_url': self.mobile_url,
            'cover': self.cover,
            'hot': self.hot,
            'trend_score': self.trend_score,
            'source_time': self.source_time,
            'expire_time': self.expire_time,
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
        # 处理时间字段兼容性
        if 'source_time' not in data and ('timestamp' in data or 'fetch_time' in data):
            # 优先使用fetch_time，其次使用timestamp
            data['source_time'] = data.get('fetch_time', data.get('timestamp', int(time.time())))

        # 创建实例
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            platform=data.get('platform'),
            description=data.get('description'),
            url=data.get('url'),
            mobile_url=data.get('mobile_url'),
            cover=data.get('cover'),
            hot=data.get('hot', 0),
            trend_score=data.get('trend_score', 0.0),
            source_time=data.get('source_time', int(time.time())),
            expire_time=data.get('expire_time', int(time.time()) + 7 * 24 * 60 * 60),
        )
