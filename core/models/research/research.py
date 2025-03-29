"""研究报告模型

该模块定义了与研究过程相关的核心数据模型，包括继承基础研究模型并添加ID的具体业务模型。
这些模型用于表示和传递研究过程中产生的数据，与话题模型紧密关联，并可用于持久化存储。
"""

import uuid
from typing import List, Dict, Optional, Any
from pydantic import Field, ConfigDict
from datetime import datetime

from .basic_research import BasicResearch


class TopicResearch(BasicResearch):
    """话题研究结果模型

    表示完整的研究结果，包含背景信息、专家见解、关键发现等。
    与特定话题相关联，继承自BasicResearch并添加id和topic_id字段。
    这是与数据库交互的主要模型，用于持久化存储。
    """
    # 增加自己的ID字段，这是TopicResearch与BasicResearch的主要区别
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="研究报告唯一ID")

    # 关联信息
    topic_id: str = Field(..., description="关联的话题ID")

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "id": "research_001",
                "topic_id": "topic_001",
                "content_type": "tech_tutorial",
                "title": "Python异步编程最佳实践研究",
                "background": "异步编程是现代应用开发中的重要技术，尤其在IO密集型应用中...",
                "expert_insights": [
                    {
                        "expert_name": "David Beazley",
                        "content": "异步编程最大的挑战在于思维模式的转变...",
                        "field": "Python开发",
                        "credentials": "知名Python演讲者，著有多本Python图书",
                        "source": {
                            "name": "PyCon 2023演讲",
                            "url": "https://example.com/pycon2023",
                            "reliability_score": 0.9
                        }
                    }
                ],
                "key_findings": [
                    {
                        "content": "asyncio在IO密集型应用中可提升性能5-10倍",
                        "importance": 0.8,
                        "sources": [
                            {
                                "name": "Python官方文档",
                                "url": "https://docs.python.org/3/library/asyncio.html",
                                "reliability_score": 1.0
                            }
                        ]
                    }
                ],
                "research_timestamp": "2023-08-15T14:30:00"
            }
        }
    )

    @classmethod
    def from_basic_research(cls, basic_research: BasicResearch, topic_id: str, research_id: Optional[str] = None) -> 'TopicResearch':
        """从BasicResearch创建TopicResearch实例

        将不含ID的基础研究对象转换为包含ID的话题研究对象

        Args:
            basic_research: 基础研究结果
            topic_id: 话题ID
            research_id: 研究ID（可选）

        Returns:
            TopicResearch: 话题研究对象
        """
        # 转换为字典以便修改
        data = basic_research.model_dump()

        # 添加必要字段
        data["topic_id"] = topic_id
        if research_id:
            data["id"] = research_id

        # 创建并返回新实例
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，包含ID字段"""
        # 获取基础字段
        result = {
            "id": self.id,
            "topic_id": self.topic_id,
            "title": self.title,
            "content_type": self.content_type,
            "background": self.background,
            "expert_insights": [insight.model_dump() for insight in self.expert_insights],
            "key_findings": [kf.model_dump() for kf in self.key_findings],
            "sources": [s.model_dump() for s in self.sources],
            "data_analysis": self.data_analysis,
            "research_timestamp": self.research_timestamp.isoformat(),
            "summary": self.summary,
            "report": self.report,
            "metadata": self.metadata
        }
        return result
