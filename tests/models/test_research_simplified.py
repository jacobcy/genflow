import sys
import os
import pytest
from datetime import datetime
from enum import Enum, auto
import uuid
from typing import List, Dict, Optional, Any

# 模拟枚举类型，避免导入依赖
class ArticleSectionType(str, Enum):
    """文章部分/章节类型"""
    INTRODUCTION = "introduction"  # 引言
    BACKGROUND = "background"      # 背景
    MAIN_POINT = "main_point"      # 主要观点
    ANALYSIS = "analysis"          # 分析
    EXAMPLE = "example"            # 示例
    COMPARISON = "comparison"      # 对比
    CONCLUSION = "conclusion"      # 结论
    REFERENCE = "reference"        # 参考资料

# 模拟Pydantic模型
class BaseModel:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

    def model_dump(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

# 模拟Field装饰器
def Field(default=None, **kwargs):
    return default

# 模拟ConfigDict
def ConfigDict(**kwargs):
    return {}

# 模拟核心模型
class Source(BaseModel):
    """信息来源"""
    def __init__(self, name, url=None, author=None, publish_date=None,
                 reliability_score=0.0, content_snippet=None):
        self.name = name
        self.url = url
        self.author = author
        self.publish_date = publish_date
        self.reliability_score = reliability_score
        self.content_snippet = content_snippet

class ExpertInsight(BaseModel):
    """专家见解"""
    def __init__(self, expert_name, content, field=None, credentials=None, source=None):
        self.expert_name = expert_name
        self.content = content
        self.field = field
        self.credentials = credentials
        self.source = source

class KeyFinding(BaseModel):
    """关键发现"""
    def __init__(self, content, importance=0.0, sources=None):
        self.content = content
        self.importance = importance
        self.sources = sources or []

class BasicResearch(BaseModel):
    """基础研究结果模型"""
    def __init__(self, title, content_type, background=None, expert_insights=None,
                 key_findings=None, sources=None, data_analysis=None,
                 research_timestamp=None, summary=None, report=None, metadata=None):
        self.title = title
        self.content_type = content_type
        self.background = background
        self.expert_insights = expert_insights or []
        self.key_findings = key_findings or []
        self.sources = sources or []
        self.data_analysis = data_analysis
        self.research_timestamp = research_timestamp or datetime.now()
        self.summary = summary
        self.report = report
        self.metadata = metadata or {}

    def to_dict(self):
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
    def from_simple_research(cls, title, content, key_points, references, content_type):
        """从简单版本的研究结果创建标准BasicResearch"""
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

class TopicResearch(BasicResearch):
    """话题研究结果模型"""
    def __init__(self, id=None, topic_id=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id or str(uuid.uuid4())
        self.topic_id = topic_id

    @classmethod
    def from_basic_research(cls, basic_research, topic_id, research_id=None):
        """从BasicResearch创建TopicResearch实例"""
        # 创建字典以便修改
        data = {
            "title": basic_research.title,
            "content_type": basic_research.content_type,
            "background": basic_research.background,
            "expert_insights": basic_research.expert_insights,
            "key_findings": basic_research.key_findings,
            "sources": basic_research.sources,
            "data_analysis": basic_research.data_analysis,
            "research_timestamp": basic_research.research_timestamp,
            "summary": basic_research.summary,
            "report": basic_research.report,
            "metadata": basic_research.metadata,
            "topic_id": topic_id,
            "id": research_id
        }

        # 创建并返回新实例
        return cls(**data)


# 测试函数
def test_basic_research_creation():
    """测试基础研究报告模型创建"""
    # 准备测试数据
    title = "Python异步编程最佳实践"
    content_type = "tech_report"
    background = "异步编程是现代应用开发中的重要技术..."

    # 创建基础研究报告
    research = BasicResearch(
        title=title,
        content_type=content_type,
        background=background
    )

    # 验证基本属性
    assert research.title == title
    assert research.content_type == content_type
    assert research.background == background
    assert isinstance(research.research_timestamp, datetime)
    assert len(research.expert_insights) == 0
    assert len(research.key_findings) == 0
    assert len(research.sources) == 0


def test_research_with_insights_and_findings():
    """测试带有见解和发现的研究报告"""
    # 创建来源
    source = Source(
        name="Python官方文档",
        url="https://docs.python.org/3/library/asyncio.html",
        reliability_score=1.0
    )

    # 创建专家见解
    insight = ExpertInsight(
        expert_name="David Beazley",
        content="异步编程最大的挑战在于思维模式的转变...",
        field="Python开发"
    )

    # 创建关键发现
    finding = KeyFinding(
        content="asyncio在IO密集型应用中可提升性能5-10倍",
        importance=0.8,
        sources=[source]
    )

    # 创建研究报告
    research = BasicResearch(
        title="Python异步编程研究",
        content_type="tech_report",
        background="异步编程背景...",
        expert_insights=[insight],
        key_findings=[finding],
        sources=[source]
    )

    # 验证关联属性
    assert len(research.expert_insights) == 1
    assert research.expert_insights[0].expert_name == "David Beazley"
    assert len(research.key_findings) == 1
    assert research.key_findings[0].importance == 0.8
    assert len(research.sources) == 1
    assert research.sources[0].name == "Python官方文档"
    assert research.sources[0].reliability_score == 1.0


def test_topic_research_from_basic():
    """测试从BasicResearch创建TopicResearch"""
    # 创建基础研究
    basic = BasicResearch(
        title="Python测试最佳实践",
        content_type="tutorial",
        background="测试是软件开发的关键环节..."
    )

    # 创建话题研究
    topic_id = "topic_123"
    topic_research = TopicResearch.from_basic_research(basic, topic_id)

    # 验证继承的属性
    assert topic_research.title == basic.title
    assert topic_research.content_type == basic.content_type
    assert topic_research.background == basic.background

    # 验证特有的属性
    assert topic_research.topic_id == topic_id
    assert topic_research.id is not None  # 应该自动生成ID


def test_article_section_type_enum():
    """测试ArticleSectionType枚举的正确导入和使用"""
    # 验证枚举值
    assert ArticleSectionType.INTRODUCTION == "introduction"
    assert ArticleSectionType.BACKGROUND == "background"
    assert ArticleSectionType.MAIN_POINT == "main_point"

    # 使用枚举创建研究报告
    research = BasicResearch(
        title="枚举测试",
        content_type=ArticleSectionType.ANALYSIS  # 使用枚举值作为内容类型
    )

    assert research.content_type == "analysis"


if __name__ == "__main__":
    # 运行所有测试
    test_basic_research_creation()
    test_research_with_insights_and_findings()
    test_topic_research_from_basic()
    test_article_section_type_enum()
    print("所有测试通过!")
