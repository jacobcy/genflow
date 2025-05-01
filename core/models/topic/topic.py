"""话题数据模型

包含话题的基本信息结构和相关功能。
话题是内容创作的主题，包含标题、描述等基本信息。
所有话题都来自外部抓取，不包含创建话题的功能。
"""

import uuid
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

from loguru import logger


class Topic(BaseModel):
    """话题模型，包含话题的基本信息

    话题是内容创作的基础，提供标题、描述等信息。
    该模型不包含创建话题的功能，仅用于表示外部抓取的话题数据。
    """
    # 基本信息
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="话题唯一ID")
    title: str = Field(..., description="话题标题")
    description: str = Field(default="", description="话题描述")
    platform: str = Field(default="", description="目标平台")

    # 时间相关字段
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    source_time: Optional[int] = Field(default=None, description="来源时间戳")
    expire_time: Optional[int] = Field(default=None, description="过期时间戳")

    # URL相关字段
    url: str = Field(default="", description="话题链接")
    mobile_url: str = Field(default="", description="移动端链接")

    # 内容特性字段
    hot: int = Field(default=0, description="热度值")
    cover: str = Field(default="", description="封面图片URL")

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
        data = self.model_dump()

        # 确保时间字段正确
        if self.source_time is None:
            data['source_time'] = int(time.time())
        if self.expire_time is None:
            # 默认7天后过期
            data['expire_time'] = int(time.time()) + 7 * 24 * 60 * 60

        return data

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
                "url": "https://example.com/topics/python-async",
                "mobile_url": "https://m.example.com/topics/python-async",
                "hot": 100,
                "cover": "https://example.com/images/python-async.jpg",
                "platform": "medium"
            }
        }
