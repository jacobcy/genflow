"""研究结果模型

该模块定义了与研究团队相关的数据模型，包括研究结果、文章结构和反馈等。
这些模型用于在系统中表示和传递研究过程中产生的数据。
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ArticleSectionType(Enum):
    """文章部分类型"""
    INTRODUCTION = "introduction"  # 引言
    BACKGROUND = "background"      # 背景
    MAIN_POINT = "main_point"      # 主要观点
    ANALYSIS = "analysis"          # 分析
    EXAMPLE = "example"            # 示例
    COMPARISON = "comparison"      # 对比
    CONCLUSION = "conclusion"      # 结论
    REFERENCE = "reference"        # 参考资料

@dataclass
class ArticleSection:
    """文章部分结构

    表示文章的一个部分或一个段落，包含标题、内容和类型。
    """
    title: str
    content: str
    section_type: ArticleSectionType
    subsections: List['ArticleSection'] = field(default_factory=list)
    order: int = 0

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "title": self.title,
            "content": self.content,
            "section_type": self.section_type.value,
            "order": self.order,
            "subsections": [s.to_dict() for s in self.subsections]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ArticleSection':
        """从字典创建实例"""
        section = cls(
            title=data["title"],
            content=data["content"],
            section_type=ArticleSectionType(data["section_type"]),
            order=data.get("order", 0)
        )

        if "subsections" in data:
            section.subsections = [cls.from_dict(s) for s in data["subsections"]]

        return section

@dataclass
class Source:
    """信息来源

    表示研究过程中使用的信息来源，包括来源名称、URL和可靠性评分。
    """
    name: str
    url: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    reliability_score: float = 0.0
    content_snippet: Optional[str] = None

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "name": self.name,
            "url": self.url,
            "author": self.author,
            "publish_date": self.publish_date,
            "reliability_score": self.reliability_score,
            "content_snippet": self.content_snippet
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Source':
        """从字典创建实例"""
        return cls(
            name=data["name"],
            url=data.get("url"),
            author=data.get("author"),
            publish_date=data.get("publish_date"),
            reliability_score=data.get("reliability_score", 0.0),
            content_snippet=data.get("content_snippet")
        )

@dataclass
class ExpertInsight:
    """专家见解

    表示从专家那里收集到的见解或观点。
    """
    expert_name: str
    content: str
    field: Optional[str] = None
    credentials: Optional[str] = None
    source: Optional[Source] = None

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "expert_name": self.expert_name,
            "content": self.content,
            "field": self.field,
            "credentials": self.credentials,
            "source": self.source.to_dict() if self.source else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ExpertInsight':
        """从字典创建实例"""
        return cls(
            expert_name=data["expert_name"],
            content=data["content"],
            field=data.get("field"),
            credentials=data.get("credentials"),
            source=Source.from_dict(data["source"]) if data.get("source") else None
        )

@dataclass
class KeyFinding:
    """关键发现

    表示研究过程中的一个关键发现或结论。
    """
    content: str
    importance: float = 0.0  # 0.0-1.0的重要性评分
    sources: List[Source] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "content": self.content,
            "importance": self.importance,
            "sources": [s.to_dict() for s in self.sources]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'KeyFinding':
        """从字典创建实例"""
        finding = cls(
            content=data["content"],
            importance=data.get("importance", 0.0)
        )

        if "sources" in data:
            finding.sources = [Source.from_dict(s) for s in data["sources"]]

        return finding

@dataclass
class ResearchResult:
    """研究结果

    表示完整的研究结果，包含背景信息、专家见解、关键发现等。
    """
    topic: str
    background: Optional[str] = None
    expert_insights: List[ExpertInsight] = field(default_factory=list)
    key_findings: List[KeyFinding] = field(default_factory=list)
    sources: List[Source] = field(default_factory=list)
    data_analysis: Optional[str] = None
    research_timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "topic": self.topic,
            "background": self.background,
            "expert_insights": [e.to_dict() for e in self.expert_insights],
            "key_findings": [f.to_dict() for f in self.key_findings],
            "sources": [s.to_dict() for s in self.sources],
            "data_analysis": self.data_analysis,
            "research_timestamp": self.research_timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ResearchResult':
        """从字典创建实例"""
        result = cls(
            topic=data["topic"],
            background=data.get("background"),
            data_analysis=data.get("data_analysis")
        )

        if "expert_insights" in data:
            result.expert_insights = [ExpertInsight.from_dict(e) for e in data["expert_insights"]]

        if "key_findings" in data:
            result.key_findings = [KeyFinding.from_dict(f) for f in data["key_findings"]]

        if "sources" in data:
            result.sources = [Source.from_dict(s) for s in data["sources"]]

        if "research_timestamp" in data:
            result.research_timestamp = datetime.fromisoformat(data["research_timestamp"])

        return result

@dataclass
class Article:
    """文章结构

    表示完整的文章结构，由多个部分组成。
    """
    title: str
    description: str
    sections: List[ArticleSection] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    word_count: int = 0

    def to_dict(self) -> Dict:
        """转换为字典表示"""
        return {
            "title": self.title,
            "description": self.description,
            "sections": [s.to_dict() for s in self.sections],
            "tags": self.tags,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "word_count": self.word_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Article':
        """从字典创建实例"""
        article = cls(
            title=data["title"],
            description=data["description"],
            tags=data.get("tags", []),
            author=data.get("author"),
            word_count=data.get("word_count", 0)
        )

        if "sections" in data:
            article.sections = [ArticleSection.from_dict(s) for s in data["sections"]]

        if "created_at" in data:
            article.created_at = datetime.fromisoformat(data["created_at"])

        return article
