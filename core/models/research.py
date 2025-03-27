"""研究结果模型

该模块定义了与研究过程相关的数据模型，包括研究结果和反馈等。
这些模型用于表示和传递研究过程中产生的数据，与话题模型紧密关联。
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .enums import ArticleSectionType

class ArticleSection(BaseModel):
    """文章部分结构

    表示文章的一个部分或一个段落，包含标题、内容和类型。
    """
    title: str = Field(..., description="部分标题")
    content: str = Field(..., description="部分内容")
    section_type: ArticleSectionType = Field(..., description="部分类型")
    subsections: List['ArticleSection'] = Field(default_factory=list, description="子部分列表")
    order: int = Field(default=0, description="排序序号")

class Source(BaseModel):
    """信息来源

    表示研究过程中使用的信息来源，包括来源名称、URL和可靠性评分。
    """
    name: str = Field(..., description="来源名称")
    url: Optional[str] = Field(default=None, description="来源URL")
    author: Optional[str] = Field(default=None, description="作者")
    publish_date: Optional[str] = Field(default=None, description="发布日期")
    reliability_score: float = Field(default=0.0, description="可靠性评分(0-1)")
    content_snippet: Optional[str] = Field(default=None, description="内容摘要")

class ExpertInsight(BaseModel):
    """专家见解

    表示从专家那里收集到的见解或观点。
    """
    expert_name: str = Field(..., description="专家姓名")
    content: str = Field(..., description="见解内容")
    field: Optional[str] = Field(default=None, description="专业领域")
    credentials: Optional[str] = Field(default=None, description="资质证明")
    source: Optional[Source] = Field(default=None, description="来源信息")

class KeyFinding(BaseModel):
    """关键发现

    表示研究过程中的一个关键发现或结论。
    """
    content: str = Field(..., description="发现内容")
    importance: float = Field(default=0.0, description="重要性评分(0-1)")
    sources: List[Source] = Field(default_factory=list, description="支持此发现的来源列表")

class ArticleOutlineItem(BaseModel):
    """文章大纲项

    表示文章大纲中的一个项目，包含标题、内容摘要和类型。
    """
    title: str = Field(..., description="标题")
    summary: str = Field(default="", description="内容摘要")
    section_type: ArticleSectionType = Field(..., description="部分类型")
    subsections: List['ArticleOutlineItem'] = Field(default_factory=list, description="子项列表")
    order: int = Field(default=0, description="排序序号")

class TopicResearch(BaseModel):
    """话题研究结果

    表示完整的研究结果，包含背景信息、专家见解、关键发现等。
    与特定话题和内容类型相关联。
    """
    topic_id: str = Field(..., description="关联的话题ID")
    content_type: str = Field(..., description="内容类型")

    title: str = Field(..., description="研究标题")
    background: Optional[str] = Field(default=None, description="背景信息")

    expert_insights: List[ExpertInsight] = Field(default_factory=list, description="专家见解列表")
    key_findings: List[KeyFinding] = Field(default_factory=list, description="关键发现列表")
    sources: List[Source] = Field(default_factory=list, description="信息来源列表")

    data_analysis: Optional[str] = Field(default=None, description="数据分析结果")
    research_timestamp: datetime = Field(default_factory=datetime.now, description="研究时间")

    article_outline: Optional[List[ArticleOutlineItem]] = Field(default=None, description="文章大纲")

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v):
        """验证内容类型"""
        # 此处可添加内容类型验证逻辑
        # 例如检查ContentType.get_content_type(v)是否返回有效实例
        return v

    class Config:
        """模型配置"""
        json_schema_extra = {
            "example": {
                "topic_id": "topic_001",
                "content_type": "tech_tutorial",
                "title": "Python异步编程最佳实践",
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
                "research_timestamp": "2023-08-15T14:30:00",
                "article_outline": [
                    {
                        "title": "引言",
                        "summary": "介绍异步编程的重要性和Python中的演变历程",
                        "section_type": "introduction",
                        "order": 1
                    },
                    {
                        "title": "异步编程基础概念",
                        "summary": "解释协程、事件循环等核心概念",
                        "section_type": "background",
                        "order": 2,
                        "subsections": [
                            {
                                "title": "协程详解",
                                "summary": "深入解释协程的工作原理",
                                "section_type": "analysis",
                                "order": 1
                            }
                        ]
                    }
                ]
            }
        }
