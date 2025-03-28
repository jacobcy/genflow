"""基础文章数据模型

该模型为不依赖话题和大纲的简化文章模型，适用于直接文本输入和风格化处理。
"""
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator

from .article import Section

class BasicArticle(BaseModel):
    """基础文章模型 - 简化版文章，无需话题和大纲依赖"""
    # 基础标识
    id: str = Field(default_factory=lambda: f"article_{datetime.now().strftime('%Y%m%d%H%M%S')}", description="文章ID")

    # 核心内容
    title: str = Field(..., description="文章标题")
    summary: Optional[str] = Field(default="", description="文章摘要")
    content: Optional[str] = Field(default="", description="文章正文内容（纯文本格式）")
    sections: List[Section] = Field(default_factory=list, description="文章章节（结构化格式）")
    tags: List[str] = Field(default_factory=list, description="文章标签")
    keywords: List[str] = Field(default_factory=list, description="关键词")

    # 分类与类型
    content_type: str = Field(default="default", description="内容类型")
    categories: List[str] = Field(default_factory=list, description="文章分类")

    # 元数据
    author: str = Field(default="AI", description="作者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    word_count: int = Field(default=0, description="字数统计")
    read_time: int = Field(default=0, description="阅读时间(分钟)")

    # 风格相关
    style_id: Optional[str] = Field(default=None, description="风格ID")

    # 平台相关
    platform_id: Optional[str] = Field(default=None, description="目标平台ID")

    # 其他元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    def __init__(self, **data):
        super().__init__(**data)
        # 如果提供了content但没有sections，则尝试创建基本section
        if self.content and not self.sections:
            self.sections = [
                Section(
                    title="正文",
                    content=self.content,
                    order=1
                )
            ]
        # 如果没有提供summary但有content，从content中提取摘要
        if not self.summary and self.content:
            # 简单截取前100个字符作为摘要
            self.summary = self.content[:100] + ("..." if len(self.content) > 100 else "")

        # 初始计算一次指标
        self.calculate_metrics()

    def update_content(self, new_content: str) -> None:
        """更新文章内容

        Args:
            new_content: 新内容
        """
        self.content = new_content
        # 更新section
        if self.sections:
            # 如果已经有section，则更新第一个section
            self.sections[0].content = new_content
        else:
            # 否则创建新section
            self.sections = [
                Section(
                    title="正文",
                    content=new_content,
                    order=1
                )
            ]
        self.updated_at = datetime.now()
        self.calculate_metrics()

    def calculate_metrics(self) -> Dict[str, Any]:
        """计算文章指标

        Returns:
            Dict: 文章指标统计
        """
        # 计算总字数
        if self.sections:
            total_words = len(self.title) + sum(len(section.title) + len(section.content) for section in self.sections)
        else:
            total_words = len(self.title) + len(self.summary) + len(self.content)

        # 估算阅读时间 (假设平均阅读速度400字/分钟)
        read_time = max(1, round(total_words / 400))

        # 更新指标
        self.word_count = total_words
        self.read_time = read_time

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(self.sections)
        }

    @field_validator('sections')
    @classmethod
    def sort_sections(cls, sections: List[Section]) -> List[Section]:
        """确保章节按顺序排序

        Args:
            sections: 章节列表

        Returns:
            List[Section]: 排序后的章节列表
        """
        return sorted(sections, key=lambda x: x.order)

    @classmethod
    def from_text(cls, text: str, title: Optional[str] = None) -> "BasicArticle":
        """从纯文本创建基础文章

        Args:
            text: 文本内容
            title: 标题（可选，如果不提供则使用文本的前20个字符）

        Returns:
            BasicArticle: 创建的基础文章对象
        """
        if not title:
            # 使用文本前20个字符作为标题
            title = text[:20] + ("..." if len(text) > 20 else "")

        return cls(
            title=title,
            content=text
        )

    @classmethod
    def from_article(cls, article: Any) -> "BasicArticle":
        """从完整Article对象创建BasicArticle

        Args:
            article: Article对象

        Returns:
            BasicArticle: 创建的基础文章对象
        """
        content = ""
        if hasattr(article, 'sections') and article.sections:
            # 将section内容合并为单个文本
            content = "\n\n".join([f"## {section.title}\n{section.content}" for section in article.sections])

        data = {
            "title": article.title,
            "summary": getattr(article, 'summary', ""),
            "content": content,
            "sections": getattr(article, 'sections', []),
            "tags": getattr(article, 'tags', []),
            "keywords": getattr(article, 'keywords', []),
            "content_type": getattr(article, 'content_type', "default"),
            "categories": getattr(article, 'categories', []),
            "author": getattr(article, 'author', "AI"),
            "style_id": getattr(article, 'style_id', None),
            "platform_id": getattr(article, 'platform_id', None),
        }

        # 如果原article有id，保留它
        if hasattr(article, 'id'):
            data["id"] = article.id

        return cls(**data)

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "article_20230501120000",
                "title": "Python异步编程简介",
                "summary": "本文简要介绍Python中的异步编程概念和实践方法。",
                "content": "Python中的异步编程主要基于asyncio库实现...",
                "tags": ["Python", "异步编程"],
                "content_type": "blog_post",
                "word_count": 1200,
                "read_time": 3
            }
        }
