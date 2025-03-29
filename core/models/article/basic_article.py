"""基础文章数据模型

该模型为不依赖话题和大纲的简化文章模型，适用于直接文本输入和风格化处理。
只包含数据结构，不包含逻辑代码。
"""
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field

from .article import Section

class BasicArticle(BaseModel):
    """基础文章模型 - 简化版文章，无需话题和大纲依赖"""

    # 基础标识 (可选)
    id: Optional[str] = Field(default=None, description="文章ID，可选")

    # 核心内容
    title: str = Field(..., description="文章标题")
    summary: str = Field(default="", description="文章摘要")
    content: str = Field(default="", description="文章正文内容（纯文本格式）")
    sections: List[Section] = Field(default_factory=list, description="文章章节（结构化格式）")
    tags: List[str] = Field(default_factory=list, description="文章标签")

    # 分类与类型
    content_type: str = Field(default="default", description="内容类型")
    categories: List[str] = Field(default_factory=list, description="文章分类")

    # 元数据
    author: str = Field(default="AI", description="作者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    word_count: int = Field(default=0, description="字数统计")
    read_time: int = Field(default=0, description="阅读时间(分钟)")

    # 其他元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    def calculate_basic_metrics(self) -> Dict[str, Any]:
        """计算基础文章指标

        Returns:
            Dict[str, Any]: 文章指标统计
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
        self.updated_at = datetime.now()

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(self.sections)
        }

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "title": "Python异步编程简介",
                "summary": "本文简要介绍Python中的异步编程概念和实践方法。",
                "content": "Python中的异步编程主要基于asyncio库实现...",
                "tags": ["Python", "异步编程"],
                "content_type": "blog_post",
                "word_count": 1200,
                "read_time": 3
            }
        }
