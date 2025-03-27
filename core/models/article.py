"""文章数据模型"""
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator
from .topic import Topic
from .article_style import ArticleStyle
from .content_type import ContentType
from .platform import Platform

class Section(BaseModel):
    """文章章节"""
    id: str = Field(default="", description="章节ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(..., description="章节顺序")
    type: str = Field(default="text", description="章节类型")
    depth: int = Field(default=1, description="章节深度")
    parent_id: Optional[str] = Field(default=None, description="父章节ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="章节元数据")

class ReviewResult(BaseModel):
    """审核结果"""
    score: float = Field(default=0.0, description="审核得分")
    comments: str = Field(default="", description="审核意见")
    reviewed_at: Optional[datetime] = Field(default=None, description="审核时间")
    reviewer: Optional[str] = Field(default=None, description="审核人")
    platform_specific_issues: List[Dict[str, Any]] = Field(default_factory=list, description="平台特定问题")
    is_approved: bool = Field(default=False, description="是否通过审核")

class Article(BaseModel):
    """文章模型 - 内容创作的核心产出"""
    # 基础标识
    id: str = Field(..., description="文章ID")
    topic_id: str = Field(..., description="关联话题ID")
    outline_id: Optional[str] = Field(default=None, description="关联大纲ID")

    # 核心内容
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    sections: List[Section] = Field(default_factory=list, description="文章章节")
    tags: List[str] = Field(default_factory=list, description="文章标签")
    keywords: List[str] = Field(default_factory=list, description="关键词")

    # 媒体元素
    cover_image: Optional[str] = Field(default=None, description="封面图URL")
    cover_image_alt: Optional[str] = Field(default=None, description="封面图替代文本")
    images: List[Dict[str, str]] = Field(default_factory=list, description="文章中的图片")

    # 分类与类型
    content_type: str = Field(default="default", description="内容类型")
    categories: List[str] = Field(default_factory=list, description="文章分类")

    # 元数据
    author: str = Field(default="AI", description="作者")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    word_count: int = Field(default=0, description="字数统计")
    read_time: int = Field(default=0, description="阅读时间(分钟)")
    version: int = Field(default=1, description="版本号")

    # 状态管理
    status: str = Field(
        default="initialized",
        description="文章状态(initialized/topic/research/outline/writing/style/review/completed/failed/cancelled)"
    )
    is_published: bool = Field(default=False, description="是否已发布")

    # 风格相关
    style_id: Optional[str] = Field(default=None, description="风格ID")

    # 平台相关
    platform_id: Optional[str] = Field(default=None, description="发布平台ID")
    platform_url: Optional[str] = Field(default=None, description="平台发布URL")

    # 审核相关
    review: ReviewResult = Field(default_factory=ReviewResult, description="审核结果")

    # 其他元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")

    def update_status(self, new_status: str) -> None:
        """更新文章状态并记录时间

        Args:
            new_status: 新状态
        """
        self.status = new_status
        self.updated_at = datetime.now()
        # 记录状态变更到元数据
        if "status_history" not in self.metadata:
            self.metadata["status_history"] = []

        self.metadata["status_history"].append({
            "status": new_status,
            "timestamp": self.updated_at.isoformat()
        })

    def calculate_metrics(self) -> Dict[str, Any]:
        """计算文章指标

        Returns:
            Dict: 文章指标统计
        """
        # 计算总字数
        total_words = len(self.title) + len(self.summary)
        for section in self.sections:
            total_words += len(section.title) + len(section.content)

        # 估算阅读时间 (假设平均阅读速度400字/分钟)
        read_time = max(1, round(total_words / 400))

        # 更新指标
        self.word_count = total_words
        self.read_time = read_time

        return {
            "word_count": total_words,
            "read_time": read_time,
            "section_count": len(self.sections),
            "image_count": len(self.images) + (1 if self.cover_image else 0)
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

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "article_001",
                "topic_id": "topic_001",
                "outline_id": "outline_001",
                "title": "Python异步编程最佳实践：从入门到精通",
                "summary": "本文详细介绍Python异步编程的核心概念、实践方法和性能优化技巧",
                "tags": ["Python", "异步编程", "编程技巧", "性能优化"],
                "content_type": "tech_tutorial",
                "categories": ["programming", "python", "tutorials"],
                "style_id": "developer_guide",
                "sections": [
                    {
                        "id": "section_001",
                        "title": "引言",
                        "content": "异步编程是现代Python开发中不可或缺的一部分...",
                        "order": 1,
                        "type": "introduction"
                    }
                ],
                "word_count": 3500,
                "read_time": 9
            }
        }
