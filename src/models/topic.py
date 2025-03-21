"""话题数据模型"""
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class TopicMetrics(BaseModel):
    """话题指标"""
    search_volume: int = Field(default=0, description="搜索量")
    trend_score: float = Field(default=0.0, description="趋势分数(0-1)")
    competition_level: float = Field(default=0.0, description="竞争程度(0-1)")
    estimated_value: float = Field(default=0.0, description="预估价值(0-1)")

class TopicReference(BaseModel):
    """话题参考资料"""
    url: str = Field(..., description="资料链接")
    title: str = Field(..., description="资料标题")
    source: str = Field(..., description="来源平台")
    relevance: float = Field(default=0.0, description="相关度(0-1)")
    
class Topic(BaseModel):
    """话题模型"""
    id: str = Field(..., description="话题ID")
    title: str = Field(..., description="话题标题")
    description: str = Field(..., description="话题描述")
    category: str = Field(..., description="话题分类")
    tags: List[str] = Field(default_list=[], description="话题标签")
    
    # 评估数据
    metrics: TopicMetrics = Field(default_factory=TopicMetrics, description="话题指标")
    references: List[TopicReference] = Field(default_list=[], description="参考资料")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    status: str = Field(default="pending", description="状态(pending/approved/rejected)")
    
    # 人工反馈
    human_feedback: Optional[Dict] = Field(default=None, description="人工反馈信息")
    
    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "id": "topic_001",
                "title": "Python异步编程最佳实践",
                "description": "探讨Python异步编程的发展、应用场景和最佳实践",
                "category": "技术",
                "tags": ["Python", "异步编程", "并发"],
                "metrics": {
                    "search_volume": 1000,
                    "trend_score": 0.8,
                    "competition_level": 0.6,
                    "estimated_value": 0.75
                },
                "references": [
                    {
                        "url": "https://docs.python.org/3/library/asyncio.html",
                        "title": "asyncio — Asynchronous I/O",
                        "source": "Python官方文档",
                        "relevance": 0.95
                    }
                ],
                "status": "pending",
                "human_feedback": {
                    "interest_level": 0.9,
                    "priority": "high",
                    "notes": "需要重点关注性能优化部分"
                }
            }
        } 