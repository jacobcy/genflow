"""文章大纲模型

该模块定义了文章大纲的数据模型，作为话题到文章的中间环节，
用于结构化组织文章内容，支持文章创作过程。
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .enums import ArticleSectionType

class OutlineSection(BaseModel):
    """大纲章节

    文章大纲中的章节，包含标题、内容概要、类型和关键点等信息。
    """
    title: str = Field(..., description="章节标题")
    content: str = Field(default="", description="章节概要内容")
    order: int = Field(default=0, description="章节顺序")
    section_type: ArticleSectionType = Field(
        default=ArticleSectionType.MAIN_POINT,
        description="章节类型"
    )
    subsections: List['OutlineSection'] = Field(
        default_factory=list,
        description="子章节"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="关键要点"
    )
    references: List[str] = Field(
        default_factory=list,
        description="参考资料"
    )

class ArticleOutline(BaseModel):
    """文章大纲模型

    作为Topic和Article之间的桥梁，用于结构化规划文章内容。
    直接关联到特定话题，并为后续文章生成提供框架。
    """
    id: str = Field(..., description="大纲ID")
    topic_id: str = Field(..., description="关联话题ID")
    content_type: str = Field(default="default", description="内容类型名称")
    title: str = Field(..., description="文章标题")
    summary: str = Field(..., description="文章摘要")
    sections: List[OutlineSection] = Field(
        default_factory=list,
        description="大纲章节列表"
    )
    tags: List[str] = Field(default_factory=list, description="文章标签")

    # 大纲特有字段
    research_notes: List[str] = Field(
        default_factory=list,
        description="研究笔记"
    )
    key_insights: List[str] = Field(
        default_factory=list,
        description="核心见解"
    )
    target_word_count: int = Field(
        default=0,
        description="目标字数"
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型"""
        # 此处可添加内容类型验证逻辑
        return v

    def to_article_sections(self) -> List[Dict]:
        """将大纲转换为文章章节列表

        用于从大纲创建文章时，将大纲章节转换为文章章节格式。

        Returns:
            List[Dict]: 文章章节列表
        """
        sections = []
        for section in self.sections:
            sections.append({
                "title": section.title,
                "content": section.content or f"# {section.title}\n\n待撰写内容...",
                "order": section.order
            })
            # 可以选择是否包含子章节
        return sections

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "outline_001",
                "topic_id": "topic_001",
                "content_type": "tech_tutorial",
                "title": "Python异步编程最佳实践：从入门到精通",
                "summary": "本文详细介绍Python异步编程的核心概念、实践方法和性能优化技巧",
                "tags": ["Python", "异步编程", "并发"],
                "sections": [
                    {
                        "title": "引言",
                        "content": "介绍异步编程的重要性和Python中的演变历程",
                        "order": 1,
                        "section_type": "introduction",
                        "key_points": [
                            "异步编程的重要性",
                            "Python异步编程的发展历程"
                        ]
                    },
                    {
                        "title": "异步编程基础",
                        "content": "解释协程、事件循环等核心概念",
                        "order": 2,
                        "section_type": "main_point",
                        "key_points": [
                            "协程的概念和原理",
                            "事件循环机制",
                            "async/await语法"
                        ],
                        "subsections": [
                            {
                                "title": "协程详解",
                                "content": "深入解释协程的工作原理",
                                "order": 1,
                                "section_type": "analysis"
                            }
                        ]
                    }
                ],
                "research_notes": [
                    "需要补充更多实际应用案例",
                    "考虑添加性能对比数据"
                ],
                "key_insights": [
                    "异步编程可显著提升I/O密集型应用性能",
                    "合理使用异步编程需要考虑场景适用性"
                ],
                "target_word_count": 3000,
                "created_at": "2023-08-15T10:30:00"
            }
        }
