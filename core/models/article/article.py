"""文章数据模型

定义文章的数据结构，包含文章的基本信息、章节、元数据等。
只包含数据结构，不包含逻辑代码。
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Section(BaseModel):
    """文章章节"""
    id: str = Field(default="", description="章节ID")
    title: str = Field(..., description="章节标题")
    content: str = Field(..., description="章节内容")
    order: int = Field(..., description="章节顺序")
    type: str = Field(default="text", description="章节类型")
    parent_id: Optional[str] = Field(default=None, description="父章节ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="章节元数据")

# 引入BasicArticle的导入移到这里以避免循环导入
from .basic_article import BasicArticle

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
    content: str = Field(default="", description="文章正文内容（纯文本格式）")

    # 分类与类型
    content_type: str = Field(default="default", description="内容类型")
    categories: List[str] = Field(default_factory=list, description="文章分类")

    # 媒体元素
    cover_image: Optional[str] = Field(default=None, description="封面图URL")
    cover_image_alt: Optional[str] = Field(default=None, description="封面图替代文本")
    images: List[Dict[str, str]] = Field(default_factory=list, description="文章中的图片")

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
    feedback: Optional[str] = Field(default=None, description="审核反馈")

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
            Dict[str, Any]: 文章指标统计
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

    @classmethod
    def from_basic_article(cls, basic: BasicArticle, topic_id: str, article_id: Optional[str] = None) -> "Article":
        """从BasicArticle创建Article实例

        Args:
            basic: 基础文章对象
            topic_id: 话题ID
            article_id: 文章ID（可选）

        Returns:
            Article: 文章对象
        """
        article_data = basic.dict()

        # 添加必要字段
        article_data["topic_id"] = topic_id
        if article_id:
            article_data["id"] = article_id
        elif basic.id:
            article_data["id"] = basic.id
        else:
            from uuid import uuid4
            article_data["id"] = str(uuid4())

        return cls(**article_data)

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
