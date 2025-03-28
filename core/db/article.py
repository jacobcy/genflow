from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any, Optional
from datetime import datetime
import json
import time

from core.db.session import Base
from core.db.utils import JSONEncodedDict

class Article(Base):
    """文章数据库模型"""
    __tablename__ = "article"
    __table_args__ = {'extend_existing': True}  # 允许重新定义已存在的表

    id = Column(String(50), primary_key=True, index=True)
    topic_id = Column(String(50), nullable=False, index=True)
    outline_id = Column(String(50), nullable=True)

    # 核心内容
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    sections = Column(Text, nullable=False, default="[]")  # JSON格式存储章节
    tags = Column(Text, nullable=True, default="[]")  # JSON格式存储标签
    keywords = Column(Text, nullable=True, default="[]")  # JSON格式存储关键词

    # 媒体元素
    cover_image = Column(String(500), nullable=True)
    cover_image_alt = Column(String(500), nullable=True)
    images = Column(Text, nullable=True, default="[]")  # JSON格式存储图片

    # 分类与类型
    content_type = Column(String(50), nullable=False, default="default")
    categories = Column(Text, nullable=True, default="[]")  # JSON格式存储分类

    # 元数据
    author = Column(String(100), nullable=False, default="AI")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    word_count = Column(Integer, nullable=False, default=0)
    read_time = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)

    # 状态管理
    status = Column(String(50), nullable=False, default="initialized", index=True)
    is_published = Column(Boolean, nullable=False, default=False)

    # 风格相关
    style_id = Column(String(50), nullable=True)

    # 平台相关
    platform_id = Column(String(50), nullable=True)
    platform_url = Column(String(500), nullable=True)

    # 审核相关
    review = Column(Text, nullable=True, default="{}")  # JSON格式存储审核结果

    # 其他元数据
    meta_json = Column(Text, nullable=True, default="{}")  # JSON格式存储元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 文章数据字典
        """
        # 反序列化JSON字段
        try:
            sections = json.loads(self.sections) if self.sections else []
        except:
            sections = []

        try:
            tags = json.loads(self.tags) if self.tags else []
        except:
            tags = []

        try:
            keywords = json.loads(self.keywords) if self.keywords else []
        except:
            keywords = []

        try:
            images = json.loads(self.images) if self.images else []
        except:
            images = []

        try:
            review = json.loads(self.review) if self.review else {}
        except:
            review = {}

        try:
            metadata = json.loads(self.meta_json) if self.meta_json else {}
        except:
            metadata = {}

        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "outline_id": self.outline_id,
            "title": self.title,
            "summary": self.summary,
            "sections": sections,
            "tags": tags,
            "keywords": keywords,
            "cover_image": self.cover_image,
            "cover_image_alt": self.cover_image_alt,
            "images": images,
            "content_type": self.content_type,
            "categories": categories,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "word_count": self.word_count,
            "read_time": self.read_time,
            "version": self.version,
            "status": self.status,
            "is_published": self.is_published,
            "style_id": self.style_id,
            "platform_id": self.platform_id,
            "platform_url": self.platform_url,
            "review": review,
            "metadata": metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Article":
        """从字典创建模型实例

        Args:
            data: 文章数据字典

        Returns:
            Article: 文章模型实例
        """
        # 序列化JSON字段
        sections = json.dumps(data.get("sections", []))
        tags = json.dumps(data.get("tags", []))
        keywords = json.dumps(data.get("keywords", []))
        images = json.dumps(data.get("images", []))
        categories = json.dumps(data.get("categories", []))
        review = json.dumps(data.get("review", {}))
        meta_json = json.dumps(data.get("metadata", {}))

        created_at = data.get("created_at", datetime.now())
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.now()

        updated_at = data.get("updated_at", datetime.now())
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = datetime.now()

        return cls(
            id=data.get("id"),
            topic_id=data.get("topic_id"),
            outline_id=data.get("outline_id"),
            title=data.get("title"),
            summary=data.get("summary"),
            sections=sections,
            tags=tags,
            keywords=keywords,
            cover_image=data.get("cover_image"),
            cover_image_alt=data.get("cover_image_alt"),
            images=images,
            content_type=data.get("content_type", "default"),
            categories=categories,
            author=data.get("author", "AI"),
            created_at=created_at,
            updated_at=updated_at,
            word_count=data.get("word_count", 0),
            read_time=data.get("read_time", 0),
            version=data.get("version", 1),
            status=data.get("status", "initialized"),
            is_published=data.get("is_published", False),
            style_id=data.get("style_id"),
            platform_id=data.get("platform_id"),
            platform_url=data.get("platform_url"),
            review=review,
            meta_json=meta_json
        )

# 在文件末尾添加获取默认文章方法
def get_default_article() -> Optional[Dict[str, Any]]:
    """获取默认文章

    Returns:
        Optional[Dict]: 默认文章数据，如果不存在则返回None
    """
    from core.db.session import get_db
    db = next(get_db())
    article = db.query(Article).filter(Article.status == "completed").first()
    if article:
        return article.to_dict()
    return None
