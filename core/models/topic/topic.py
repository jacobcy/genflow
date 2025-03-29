"""话题数据模型

包含话题的基本信息结构和相关功能。
话题是内容创作的主题，包含标题、描述、关键词等信息。
"""

import uuid
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, field_validator

from loguru import logger


class Topic(BaseModel):
    """话题模型，包含话题的基本信息

    话题是内容创作的基础，提供标题、描述、关键词等信息，
    用于指导内容生成过程。
    """
    # 基本信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="话题唯一ID")
    title: str = Field(..., description="话题标题")
    description: str = Field(default="", description="话题描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="最后更新时间")

    # 分类和标签
    category: str = Field(default="general", description="话题分类")
    tags: List[str] = Field(default_factory=list, description="话题标签")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")

    # 内容相关属性
    language: str = Field(default="zh-CN", description="语言")
    content_type: str = Field(default="article", description="内容类型，如article、video等")
    platform: str = Field(default="", description="目标平台")

    # 额外属性
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据，存储附加信息")
    parent_id: Optional[str] = Field(default=None, description="父话题ID，用于构建话题层次结构")

    @field_validator('id')
    def validate_id(cls, v):
        """确保ID格式正确"""
        if not v:
            return str(uuid.uuid4())
        return v

    @field_validator('title')
    def validate_title(cls, v):
        """验证标题非空且长度适当"""
        if not v:
            raise ValueError("标题不能为空")
        if len(v) > 200:
            raise ValueError("标题过长，最大允许200字符")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典

        Returns:
            Dict[str, Any]: 话题的字典表示
        """
        return self.model_dump()

    def to_json(self) -> str:
        """转换为JSON字符串

        Returns:
            str: 话题的JSON字符串表示
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)

    def update_timestamp(self):
        """更新最后修改时间"""
        self.updated_at = datetime.now()

    class Config:
        """模型配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Python异步编程最佳实践",
                "description": "探讨Python中异步编程的最佳实践和常见陷阱",
                "category": "programming",
                "tags": ["Python", "异步", "编程技巧"],
                "keywords": ["asyncio", "异步IO", "协程", "并发"],
                "language": "zh-CN",
                "content_type": "tutorial",
                "platform": "medium"
            }
        }
