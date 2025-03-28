"""文章大纲模型

该模块定义了文章大纲的数据模型，作为话题到文章的中间环节，
用于结构化组织文章内容，支持文章创作过程。
"""

from typing import List, Dict
from pydantic import Field

from .basic_outline import BasicOutline

class ArticleOutline(BasicOutline):
    """文章大纲模型

    作为Topic和Article之间的桥梁，用于结构化规划文章内容。
    继承自BasicOutline，添加了话题关联功能。
    直接关联到特定话题，并为后续文章生成提供框架。
    """
    topic_id: str = Field(..., description="关联话题ID")

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
