"""话题数据模型"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import time
import uuid

class Topic(BaseModel):
    """话题模型

    包含话题的基本信息
    """
    # 基本信息
    id: Optional[str] = Field(default=None, description="话题ID")
    title: str = Field(..., description="话题标题")
    platform: str = Field(..., description="来源平台")
    description: str = Field(default="", description="话题描述")
    url: str = Field(default="", description="原文链接")
    mobile_url: str = Field(default="", description="移动端链接")
    cover: str = Field(default="", description="封面图片")
    hot: int = Field(default=0, ge=0, lt=100000000, description="热度值")
    trend_score: float = Field(default=0.0, ge=0.0, le=1.0, description="趋势分数(0-1)")

    # 时间信息
    source_time: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="话题发布时间"
    )
    expire_time: int = Field(
        default_factory=lambda: int((datetime.now() + timedelta(days=7)).timestamp()),
        description="过期时间，默认7天"
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "id": "topic_001",
                "title": "Python异步编程最佳实践",
                "platform": "zhihu",
                "description": "探讨Python异步编程的发展历程和实践经验",
                "url": "https://www.zhihu.com/question/123456789",
                "mobile_url": "https://m.zhihu.com/question/123456789",
                "cover": "https://pic1.zhimg.com/v2-abc123.jpg",
                "hot": 10000,
                "trend_score": 0.8,
                "source_time": 1677649200,
                "expire_time": 1678254000
            }
        }
    )

    def __init__(self, **data):
        super().__init__(**data)
        # 如果没有提供ID，生成唯一ID
        if not self.id:
            # 使用uuid4().hex，与测试模拟一致
            unique_id = uuid.uuid4().hex[:8]
            self.id = f"{self.platform}_{int(time.time())}_{unique_id}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict[str, Any]: 话题数据字典
        """
        return {
            "id": self.id,
            "title": self.title,
            "platform": self.platform,
            "description": self.description,
            "url": self.url,
            "mobile_url": self.mobile_url,
            "cover": self.cover,
            "hot": self.hot,
            "trend_score": self.trend_score,
            "source_time": self.source_time,
            "expire_time": self.expire_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Topic':
        """从字典创建话题对象

        Args:
            data: 话题数据字典

        Returns:
            Topic: 话题对象
        """
        # 确保基本字段
        id = data.get('id')
        title = data.get('title', '')
        platform = data.get('platform', '')

        # 设置默认时间戳
        current_time = int(time.time())

        # 创建实例
        topic = cls(
            id=id,
            title=title,
            platform=platform,
            description=data.get('description', ''),
            url=data.get('url', ''),
            mobile_url=data.get('mobile_url', ''),
            cover=data.get('cover', ''),
            hot=data.get('hot', 0),
            trend_score=data.get('trend_score', 0.0),
            source_time=data.get('source_time', current_time),
            expire_time=data.get('expire_time', current_time + 7 * 24 * 60 * 60)  # 默认7天后过期
        )

        return topic

    def __repr__(self) -> str:
        """字符串表示

        Returns:
            str: 类的字符串表示
        """
        return f"<Topic {self.id}:{self.title} from {self.platform}>"

    def is_expired(self) -> bool:
        """检查话题是否已过期

        Returns:
            bool: 是否已过期
        """
        return int(time.time()) > self.expire_time

    def get_age_hours(self) -> float:
        """获取话题年龄（小时）

        Returns:
            float: 话题年龄，以小时为单位
        """
        return (int(time.time()) - self.source_time) / 3600
