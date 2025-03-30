"""大纲模型

定义大纲的数据结构。
大纲由标题、描述和节点树组成，用于规划内容结构。
只包含数据结构，不包含逻辑代码，与数据库无关。
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class OutlineNode(BaseModel):
    """大纲节点模型，表示大纲中的一个条目"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="节点唯一ID")
    title: str = Field(..., description="节点标题")
    level: int = Field(default=1, ge=1, le=5, description="节点级别")
    content: str = Field(default="", description="节点内容")
    children: List['OutlineNode'] = Field(default_factory=list, description="子节点列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="节点元数据")


class BasicOutline(BaseModel):
    """大纲基础模型，代表内容结构大纲的基本形态

    不包含ID和存储相关字段，专注于定义大纲的数据结构。
    具体的业务实现（如ArticleOutline）可继承此类并添加ID等字段。
    """
    title: str = Field(..., description="大纲标题")
    description: str = Field(default="", description="大纲描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 大纲类型与来源
    content_type: str = Field(default="article", description="内容类型")
    source: str = Field(default="manual", description="大纲来源")

    # 内容结构
    nodes: List[OutlineNode] = Field(default_factory=list, description="大纲节点列表")

    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="大纲元数据")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 大纲数据的字典表示
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BasicOutline":
        """从字典创建实例

        Args:
            data: 大纲数据字典

        Returns:
            BasicOutline: 大纲实例
        """
        return cls.model_validate(data)

    model_config = ConfigDict(
        json_encoders = {
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra = {
            "example": {
                "title": "深入理解Python异步编程",
                "description": "本大纲涵盖Python异步编程的核心概念和实践",
                "content_type": "tutorial",
                "nodes": [
                    {
                        "id": "node-1",
                        "title": "异步编程基础",
                        "level": 1,
                        "children": [
                            {
                                "id": "node-1-1",
                                "title": "同步vs异步",
                                "level": 2,
                                "content": "解释两种不同的编程模型"
                            }
                        ]
                    }
                ]
            }
        }
    )
