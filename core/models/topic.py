"""话题数据模型"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .category import Category
from .content_type import ContentType
import time
import uuid

class Topic(BaseModel):
    """话题模型

    包含话题的基本信息和分类数据
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
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="话题发布时间"
    )
    fetch_time: int = Field(
        default_factory=lambda: int(datetime.now().timestamp()),
        description="抓取时间"
    )
    expire_time: int = Field(
        default_factory=lambda: int((datetime.now() + timedelta(days=7)).timestamp()),
        description="过期时间，默认7天"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="更新时间"
    )

    # 分类信息
    categories: List[str] = Field(default_factory=list, description="内容分类列表")
    tags: List[str] = Field(default_factory=list, description="内容标签")
    content_type: Optional[str] = Field(default=None, description="内容类型名称")

    # 状态信息
    status: str = Field(default="pending", description="话题状态: pending, selected, rejected")

    @field_validator("platform")
    @classmethod
    def validate_platform_categories(cls, v):
        """验证平台分类"""
        categories = Category.get_platform_categories(v)
        if not categories:
            raise ValueError(f"Invalid platform: {v}")
        return v

    @field_validator("categories")
    @classmethod
    def validate_categories(cls, v, info):
        """验证内容分类列表"""
        # 检查是否是从from_dict创建的，如果是则保持空列表
        # from_dict方法会显式设置categories为空列表，而不是None
        if v == [] and 'categories' in info.data:
            return []

        if not v:
            # 如果未指定分类，使用平台的主要分类
            platform = info.data.get("platform")
            if platform:
                platform_categories = Category.get_platform_categories(platform)
                return [platform_categories[0]] if platform_categories else []
            return []

        # 验证每个分类是否有效
        invalid_categories = []
        valid_categories = []
        for category in v:
            if Category.get_category_by_name(category):
                valid_categories.append(category)
            else:
                invalid_categories.append(category)

        if invalid_categories:
            raise ValueError(f"Invalid categories: {invalid_categories}")

        return valid_categories

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型名称"""
        if v is not None:
            # 验证内容类型是否存在
            content_type = ContentType.get_content_type(v)
            if not content_type or content_type.id != v:
                raise ValueError(f"Invalid content type: {v}")
        return v

    def get_related_categories(self) -> List[Category]:
        """获取相关分类列表"""
        result = []
        seen = set()

        # 获取平台相关的所有分类
        platform_categories = Category.get_platform_categories(self.platform)
        for cat_name in platform_categories:
            if cat := Category.get_category_by_name(cat_name):
                if cat.name not in seen:
                    result.append(cat)
                    seen.add(cat.name)

        # 添加当前分类列表中的分类
        for cat_name in self.categories:
            if cat := Category.get_category_by_name(cat_name):
                if cat.name not in seen:
                    result.append(cat)
                    seen.add(cat.name)

        return result

    def get_content_type_instance(self) -> Optional[ContentType]:
        """获取内容类型实例"""
        if not self.content_type:
            # 如果未指定内容类型，尝试从分类推断
            if self.categories:
                return ContentType.from_categories(self.categories)
            return None
        return ContentType.get_content_type(self.content_type)

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
                "timestamp": 1677649200,
                "fetch_time": 1677649200,
                "expire_time": 1678254000,
                "categories": ["技术", "编程", "开发"],
                "content_type": "tech_tutorial",
                "tags": ["Python", "异步编程", "并发"]
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
            "timestamp": self.timestamp,
            "fetch_time": self.fetch_time,
            "expire_time": self.expire_time,
            "categories": self.categories,
            "tags": self.tags,
            "content_type": self.content_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            "updated_at": self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at
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

        # 处理分类字段
        # 如果categories未指定，设置为空列表
        categories = []
        if 'categories' in data and data['categories']:
            categories = data['categories']

        # 创建时避免让validator自动添加平台分类
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
            timestamp=data.get('timestamp', current_time),
            fetch_time=data.get('fetch_time', current_time),
            expire_time=data.get('expire_time', current_time + 7 * 24 * 60 * 60),  # 默认7天后过期
            categories=categories,  # 直接使用上面处理过的categories
            tags=data.get('tags', []),
            content_type=data.get('content_type'),
            status=data.get('status', 'pending')
        )

        # 处理时间字段
        if 'created_at' in data:
            if isinstance(data['created_at'], str):
                try:
                    topic.created_at = datetime.fromisoformat(data['created_at'])
                except ValueError:
                    topic.created_at = datetime.now()
            else:
                topic.created_at = data['created_at']

        if 'updated_at' in data:
            if isinstance(data['updated_at'], str):
                try:
                    topic.updated_at = datetime.fromisoformat(data['updated_at'])
                except ValueError:
                    topic.updated_at = datetime.now()
            else:
                topic.updated_at = data['updated_at']

        return topic

    def __repr__(self) -> str:
        """字符串表示

        Returns:
            str: 类的字符串表示
        """
        return f"<Topic {self.id}:{self.title} from {self.platform}>"

    def update_status(self, new_status: str) -> bool:
        """更新话题状态

        Args:
            new_status: 新状态

        Returns:
            bool: 是否成功更新
        """
        self.status = new_status
        self.updated_at = datetime.now()

        # 尝试保存到数据库
        try:
            from core.models.content_manager import ContentManager
            return ContentManager.update_topic_status(self.id, new_status)
        except ImportError:
            return True  # 如果无法导入ContentManager，则假设更新成功

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
        return (int(time.time()) - self.timestamp) / 3600
