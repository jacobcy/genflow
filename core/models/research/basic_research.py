"""基础研究报告模型

定义研究报告的基础数据结构。
包含研究内容、专家见解、关键发现等核心数据，不包含ID等存储相关字段。
只负责定义数据结构，与数据库无关。
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# 导入枚举类型
from core.models.infra.enums import ArticleSectionType


class ArticleSection(BaseModel):
    """文章部分结构

    表示文章的一个部分或一个段落，包含标题、内容和类型。
    """
    title: str = Field(..., description="部分标题")
    content: str = Field(..., description="部分内容")
    section_type: str = Field(..., description="部分类型")
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


class BasicResearch(BaseModel):
    """基础研究结果模型

    表示研究结果的基础数据结构，不包含ID和存储相关字段。
    作为纯数据模型，定义研究报告所需的各类信息。
    具体业务实现（如TopicResearch）可继承此类并添加ID等字段。
    """
    title: str = Field(..., description="研究标题")
    content_type: str = Field(..., description="内容类型")
    background: Optional[str] = Field(default=None, description="背景信息")

    expert_insights: List[ExpertInsight] = Field(default_factory=list, description="专家见解列表")
    key_findings: List[KeyFinding] = Field(default_factory=list, description="关键发现列表")
    sources: List[Source] = Field(default_factory=list, description="信息来源列表")

    data_analysis: Optional[str] = Field(default=None, description="数据分析结果")
    research_timestamp: datetime = Field(default_factory=datetime.now, description="研究时间")

    summary: Optional[str] = Field(default=None, description="研究摘要")
    report: Optional[str] = Field(default=None, description="完整研究报告")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    model_config = ConfigDict(
        json_encoders = {
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra = {
            "example": {
                "title": "Python异步编程最佳实践研究",
                "content_type": "tech_tutorial",
                "background": "异步编程是现代应用开发中的重要技术...",
                "expert_insights": [
                    {
                        "expert_name": "David Beazley",
                        "content": "异步编程最大的挑战在于思维模式的转变...",
                        "field": "Python开发"
                    }
                ],
                "key_findings": [
                    {
                        "content": "asyncio在IO密集型应用中可提升性能5-10倍",
                        "importance": 0.8
                    }
                ],
                "summary": "本研究探讨了Python异步编程的最佳实践...",
                "research_timestamp": "2023-08-15T14:30:00"
            }
        }
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
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

    @classmethod
    def from_simple_research(cls,
                          title: str,
                          content: str,
                          key_points: List[Dict],
                          references: List[Dict],
                          content_type: str) -> 'BasicResearch':
        """从简单版本的研究结果创建标准BasicResearch

        Args:
            title: 研究标题
            content: 研究内容
            key_points: 关键点列表
            references: 参考资料列表
            content_type: 内容类型

        Returns:
            BasicResearch: 基础研究结果对象
        """
        # 转换引用为Source对象
        sources = []
        for ref in references:
            source = Source(
                name=ref.get("title", "Unknown Source"),
                url=ref.get("url"),
                author=ref.get("author"),
                publish_date=ref.get("date"),
                content_snippet=ref.get("snippet"),
                reliability_score=ref.get("reliability", 0.5)
            )
            sources.append(source)

        # 转换关键点为KeyFinding对象
        key_findings = []
        for kp in key_points:
            importance = kp.get("importance", 5)
            # 将1-10的重要性转换为0-1的浮点数
            normalized_importance = importance / 10.0 if importance else 0.5

            kf = KeyFinding(
                content=kp.get("content", ""),
                importance=normalized_importance,
                sources=[]
            )
            key_findings.append(kf)

        return cls(
            title=title,
            content_type=content_type,
            summary=content[:500] + "..." if len(content) > 500 else content,
            report=content,
            key_findings=key_findings,
            sources=sources,
            metadata={
                "created_from": "simple_research",
                "created_at": datetime.now().isoformat(),
                "key_points": key_points  # 保留原始关键点数据
            }
        )
