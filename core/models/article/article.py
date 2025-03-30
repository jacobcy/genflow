"""文章模型

定义文章数据结构和基本属性，不包含业务逻辑。
业务逻辑由ArticleService处理。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class Section(BaseModel):
    """文章章节模型"""
    id: Optional[str] = None
    title: str
    content: str
    order: int = 1
    type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return self.model_dump()

class Article(BaseModel):
    """文章模型"""
    id: str
    topic_id: str
    outline_id: Optional[str] = None
    title: str
    summary: str = ""
    content: Optional[str] = None
    author: Optional[str] = None
    status: str = "draft"
    tags: List[str] = []
    categories: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: int = 1
    content_type: Optional[str] = None
    platform_id: Optional[str] = None
    style_id: Optional[str] = None
    sections: List[Section] = []
    images: List[Dict[str, Any]] = []
    videos: List[Dict[str, Any]] = []
    links: List[Dict[str, Any]] = []
    keywords: List[str] = []
    cover_image: Optional[Dict[str, Any]] = None
    word_count: int = 0
    read_time: int = 0
    language: str = "zh"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict[str, Any]: 文章数据的字典表示
        """
        return self.model_dump()

    model_config = {
        "json_schema_extra": {
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
    }
