from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Table, Integer, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict, MutableList
from typing import Dict, Any, Optional
from datetime import datetime
import json
import time
import copy

from core.models.db.session import Base, get_db

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
    content = Column(Text, nullable=True, default="")  # 添加content字段以对齐article.py
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
    feedback = Column(Text, nullable=True)  # 将review改为feedback以对齐article.py

    # 其他元数据
    metadata = Column(Text, nullable=True, default="{}")  # 将meta_json改为metadata以对齐article.py

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 文章数据字典
        """
        # 反序列化JSON字段
        try:
            # 将Column对象转为字符串后再解析
            sections_str = str(self.sections) if self.sections is not None else "[]"
            sections = json.loads(sections_str)
        except:
            sections = []

        try:
            tags_str = str(self.tags) if self.tags is not None else "[]"
            tags = json.loads(tags_str)
        except:
            tags = []

        try:
            images_str = str(self.images) if self.images is not None else "[]"
            images = json.loads(images_str)
        except:
            images = []

        try:
            categories_str = str(self.categories) if self.categories is not None else "[]"
            categories = json.loads(categories_str)
        except:
            categories = []

        try:
            metadata_str = str(self.metadata) if self.metadata is not None else "{}"
            metadata = json.loads(metadata_str)
        except:
            metadata = {}

        # 安全获取content值
        content = ""
        if hasattr(self, 'content') and self.content is not None:
            content = str(self.content)

        return {
            "id": self.id,
            "topic_id": self.topic_id,
            "outline_id": self.outline_id,
            "title": self.title,
            "summary": self.summary,
            "content": content,
            "sections": sections,
            "tags": tags,
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
            "feedback": self.feedback,
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
        metadata = json.dumps(data.get("metadata", {}))

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
            content=data.get("content", ""),
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
            feedback=data.get("feedback"),
            metadata=metadata
        )
