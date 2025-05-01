"""
测试 BasicResearch 模型

测试基础研究模型的创建、属性和方法。
"""

import pytest
from datetime import datetime

from core.models.research.basic_research import (
    BasicResearch, 
    Source, 
    ExpertInsight, 
    KeyFinding, 
    ArticleSection
)


class TestBasicResearch:
    """测试 BasicResearch 类"""

    def test_create_basic_research(self):
        """测试创建基础研究报告"""
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
        assert isinstance(research.metadata, dict)

    def test_research_with_insights_and_findings(self):
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

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建基础研究报告
        research = BasicResearch(
            title="测试研究",
            content_type="test",
            background="测试背景",
            summary="测试摘要",
            report="测试报告"
        )

        # 转换为字典
        result = research.to_dict()

        # 验证字典内容
        assert result["title"] == "测试研究"
        assert result["content_type"] == "test"
        assert result["background"] == "测试背景"
        assert result["summary"] == "测试摘要"
        assert result["report"] == "测试报告"
        assert "research_timestamp" in result
        assert "expert_insights" in result
        assert "key_findings" in result
        assert "sources" in result
        assert "metadata" in result


class TestSource:
    """测试 Source 类"""

    def test_create_source(self):
        """测试创建来源"""
        # 创建来源
        source = Source(
            name="测试来源",
            url="https://example.com",
            author="测试作者",
            publish_date="2023-01-01",
            reliability_score=0.8,
            content_snippet="测试摘要"
        )

        # 验证属性
        assert source.name == "测试来源"
        assert source.url == "https://example.com"
        assert source.author == "测试作者"
        assert source.publish_date == "2023-01-01"
        assert source.reliability_score == 0.8
        assert source.content_snippet == "测试摘要"


class TestExpertInsight:
    """测试 ExpertInsight 类"""

    def test_create_expert_insight(self):
        """测试创建专家见解"""
        # 创建来源
        source = Source(
            name="测试来源",
            url="https://example.com"
        )

        # 创建专家见解
        insight = ExpertInsight(
            expert_name="测试专家",
            content="测试内容",
            field="测试领域",
            credentials="测试资质",
            source=source
        )

        # 验证属性
        assert insight.expert_name == "测试专家"
        assert insight.content == "测试内容"
        assert insight.field == "测试领域"
        assert insight.credentials == "测试资质"
        assert insight.source == source


class TestKeyFinding:
    """测试 KeyFinding 类"""

    def test_create_key_finding(self):
        """测试创建关键发现"""
        # 创建来源
        source = Source(
            name="测试来源",
            url="https://example.com"
        )

        # 创建关键发现
        finding = KeyFinding(
            content="测试内容",
            importance=0.7,
            sources=[source]
        )

        # 验证属性
        assert finding.content == "测试内容"
        assert finding.importance == 0.7
        assert len(finding.sources) == 1
        assert finding.sources[0] == source


class TestArticleSection:
    """测试 ArticleSection 类"""

    def test_create_article_section(self):
        """测试创建文章部分"""
        # 创建子部分
        subsection = ArticleSection(
            title="子部分",
            content="子部分内容",
            section_type="subsection"
        )

        # 创建文章部分
        section = ArticleSection(
            title="测试部分",
            content="测试内容",
            section_type="test",
            subsections=[subsection],
            order=1
        )

        # 验证属性
        assert section.title == "测试部分"
        assert section.content == "测试内容"
        assert section.section_type == "test"
        assert len(section.subsections) == 1
        assert section.subsections[0].title == "子部分"
        assert section.order == 1