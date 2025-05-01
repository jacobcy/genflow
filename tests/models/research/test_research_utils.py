"""
测试研究工具函数

测试研究报告格式化和验证工具。
"""

import pytest
from datetime import datetime

from core.models.research.basic_research import BasicResearch, Source, ExpertInsight, KeyFinding
from core.models.research.research import TopicResearch
from core.models.research.utils import (
    format_research_as_markdown,
    format_research_as_json,
    validate_research_data,
    validate_source,
    get_research_completeness
)


class TestResearchFormatter:
    """测试研究报告格式化工具"""

    def test_format_research_as_markdown(self):
        """测试将研究报告格式化为Markdown格式"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            background="测试背景",
            summary="测试摘要",
            report="测试报告"
        )

        # 添加专家见解
        research.expert_insights = [
            ExpertInsight(
                expert_name="测试专家",
                content="测试内容",
                field="测试领域",
                credentials="测试资质"
            )
        ]

        # 添加来源
        source = Source(
            name="测试来源",
            url="https://example.com",
            author="测试作者",
            publish_date="2023-01-01"
        )

        # 添加关键发现
        research.key_findings = [
            KeyFinding(
                content="测试发现",
                importance=0.8,
                sources=[source]
            )
        ]

        # 添加来源
        research.sources = [source]

        # 调用方法
        result = format_research_as_markdown(research)

        # 验证结果
        assert isinstance(result, str)
        assert "# 测试研究" in result
        assert "**内容类型**: test" in result
        assert "**关联话题**: topic_001" in result
        assert "## 研究背景" in result
        assert "测试背景" in result
        assert "## 关键发现" in result
        assert "测试发现" in result
        assert "**重要性**: 80%" in result
        assert "## 专家见解" in result
        assert "### 测试专家 (测试领域)" in result
        assert "**资质**: 测试资质" in result
        assert "测试内容" in result
        assert "## 研究摘要" in result
        assert "测试摘要" in result
        assert "## 完整研究报告" in result
        assert "测试报告" in result
        assert "## 参考来源" in result
        assert "**测试来源** - [链接](https://example.com) - 作者: 测试作者" in result

    def test_format_research_as_markdown_dict(self):
        """测试将字典形式的研究报告格式化为Markdown格式"""
        # 准备测试数据
        research_dict = {
            "id": "research_001",
            "topic_id": "topic_001",
            "title": "测试研究",
            "content_type": "test",
            "background": "测试背景",
            "expert_insights": [],
            "key_findings": [],
            "sources": []
        }

        # 调用方法
        result = format_research_as_markdown(research_dict)

        # 验证结果
        assert isinstance(result, str)
        assert "# 测试研究" in result
        assert "**内容类型**: test" in result
        assert "**关联话题**: topic_001" in result
        assert "## 研究背景" in result
        assert "测试背景" in result

    def test_format_research_as_json(self):
        """测试将研究报告格式化为JSON格式"""
        # 准备测试数据
        research = BasicResearch(
            title="测试研究",
            content_type="test",
            background="测试背景"
        )

        # 调用方法
        result = format_research_as_json(research)

        # 验证结果
        assert isinstance(result, dict)
        assert result["title"] == "测试研究"
        assert result["content_type"] == "test"
        assert result["background"] == "测试背景"
        assert "research_timestamp" in result
        assert "expert_insights" in result
        assert "key_findings" in result
        assert "sources" in result
        assert "metadata" in result


class TestResearchValidator:
    """测试研究报告验证工具"""

    def test_validate_url_valid(self):
        """测试验证有效URL"""
        from core.models.research.utils.research_validator import validate_url

        # 准备测试数据
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "http://example.com/path?query=value"
        ]

        # 验证结果
        for url in valid_urls:
            assert validate_url(url) is True

    def test_validate_url_invalid(self):
        """测试验证无效URL"""
        from core.models.research.utils.research_validator import validate_url

        # 准备测试数据
        invalid_urls = [
            "",
            "example.com",
            "www.example.com",
            "ftp://example.com",
            "invalid url"
        ]

        # 验证结果
        for url in invalid_urls:
            assert validate_url(url) is False

    def test_validate_source_valid(self):
        """测试验证有效来源"""
        # 准备测试数据
        source = Source(
            name="测试来源",
            url="https://example.com",
            reliability_score=0.8
        )

        # 调用方法
        valid, errors = validate_source(source)

        # 验证结果
        assert valid is True
        assert len(errors) == 0

    def test_validate_source_invalid(self):
        """测试验证无效来源"""
        # 准备测试数据 - 无名称
        source1 = Source(
            name="",
            url="https://example.com",
            reliability_score=0.8
        )

        # 调用方法
        valid1, errors1 = validate_source(source1)

        # 验证结果
        assert valid1 is False
        assert len(errors1) > 0
        assert "来源必须包含名称" in errors1

        # 准备测试数据 - 无效URL
        source2 = Source(
            name="测试来源",
            url="invalid url",
            reliability_score=0.8
        )

        # 调用方法
        valid2, errors2 = validate_source(source2)

        # 验证结果
        assert valid2 is False
        assert len(errors2) > 0
        assert "URL格式无效" in errors2[0]

        # 准备测试数据 - 无效可靠性评分
        source3 = Source(
            name="测试来源",
            url="https://example.com",
            reliability_score=1.5
        )

        # 调用方法
        valid3, errors3 = validate_source(source3)

        # 验证结果
        assert valid3 is False
        assert len(errors3) > 0
        assert "可靠性评分必须在0-1之间" in errors3[0]

    def test_validate_source_dict(self):
        """测试验证字典形式的来源"""
        # 准备测试数据
        source_dict = {
            "name": "测试来源",
            "url": "https://example.com",
            "reliability_score": 0.8
        }

        # 调用方法
        valid, errors = validate_source(source_dict)

        # 验证结果
        assert valid is True
        assert len(errors) == 0

    def test_validate_research_data_valid(self):
        """测试验证有效研究报告"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )

        # 调用方法
        valid, errors = validate_research_data(research)

        # 验证结果
        assert valid is True
        assert len(errors) == 0

    def test_validate_research_data_invalid(self):
        """测试验证无效研究报告"""
        # 准备测试数据 - 无标题
        research1 = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="",
            content_type="test"
        )

        # 调用方法
        valid1, errors1 = validate_research_data(research1)

        # 验证结果
        assert valid1 is False
        assert len(errors1) > 0
        assert "研究报告必须包含标题" in errors1

        # 准备测试数据 - 无内容类型
        research2 = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type=""
        )

        # 调用方法
        valid2, errors2 = validate_research_data(research2)

        # 验证结果
        assert valid2 is False
        assert len(errors2) > 0
        assert "研究报告必须包含内容类型" in errors2

        # 准备测试数据 - 无ID
        research3 = TopicResearch(
            id="",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )

        # 调用方法
        valid3, errors3 = validate_research_data(research3)

        # 验证结果
        assert valid3 is False
        assert len(errors3) > 0
        assert "TopicResearch必须包含ID" in errors3

        # 准备测试数据 - 无topic_id
        research4 = TopicResearch(
            id="research_001",
            topic_id="",
            title="测试研究",
            content_type="test"
        )

        # 调用方法
        valid4, errors4 = validate_research_data(research4)

        # 验证结果
        assert valid4 is False
        assert len(errors4) > 0
        assert "TopicResearch必须包含topic_id" in errors4

    def test_validate_research_data_with_invalid_sources(self):
        """测试验证带有无效来源的研究报告"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            sources=[
                Source(name="", url="https://example.com"),  # 无名称
                Source(name="测试来源", url="invalid url")   # 无效URL
            ]
        )

        # 调用方法
        valid, errors = validate_research_data(research)

        # 验证结果
        assert valid is False
        assert len(errors) >= 2
        assert "来源 #1: 来源必须包含名称" in errors
        assert "来源 #2: URL格式无效" in errors[1]

    def test_validate_research_data_with_invalid_findings(self):
        """测试验证带有无效发现的研究报告"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            key_findings=[
                KeyFinding(content="", importance=0.8),  # 无内容
                KeyFinding(content="测试发现", importance=1.5)  # 无效重要性
            ]
        )

        # 调用方法
        valid, errors = validate_research_data(research)

        # 验证结果
        assert valid is False
        assert len(errors) >= 2
        assert "关键发现 #1 缺少内容" in errors
        assert "关键发现 #2 重要性评分必须在0-1之间" in errors[1]

    def test_validate_research_data_with_invalid_insights(self):
        """测试验证带有无效见解的研究报告"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            expert_insights=[
                ExpertInsight(expert_name="", content="测试内容"),  # 无专家姓名
                ExpertInsight(expert_name="测试专家", content="")   # 无内容
            ]
        )

        # 调用方法
        valid, errors = validate_research_data(research)

        # 验证结果
        assert valid is False
        assert len(errors) >= 2
        assert "专家见解 #1 缺少专家姓名" in errors
        assert "专家见解 #2 缺少内容" in errors[1]

    def test_validate_research_data_dict(self):
        """测试验证字典形式的研究报告"""
        # 准备测试数据
        research_dict = {
            "id": "research_001",
            "topic_id": "topic_001",
            "title": "测试研究",
            "content_type": "test"
        }

        # 调用方法
        valid, errors = validate_research_data(research_dict)

        # 验证结果
        assert valid is True
        assert len(errors) == 0

    def test_get_research_completeness(self):
        """测试获取研究报告完整度评估"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            background="测试背景",
            summary="测试摘要",
            report="测试报告",
            expert_insights=[
                ExpertInsight(
                    expert_name="测试专家",
                    content="测试内容" * 10,  # 长内容
                    field="测试领域"
                )
            ],
            key_findings=[
                KeyFinding(
                    content="测试发现",
                    importance=0.8,
                    sources=[
                        Source(
                            name="测试来源",
                            url="https://example.com"
                        )
                    ]
                )
            ],
            sources=[
                Source(
                    name="测试来源",
                    url="https://example.com"
                )
            ]
        )

        # 调用方法
        result = get_research_completeness(research)

        # 验证结果
        assert isinstance(result, dict)
        assert "overall" in result
        assert "basic_info" in result
        assert "background" in result
        assert "expert_insights" in result
        assert "key_findings" in result
        assert "sources" in result
        assert "data_analysis" in result
        assert "summary" in result
        assert "report" in result
        
        # 验证基本信息完整度
        assert result["basic_info"] == 100  # 标题和内容类型都有
        
        # 验证背景完整度
        assert result["background"] > 0  # 有背景信息
        
        # 验证专家见解完整度
        assert result["expert_insights"] > 0  # 有专家见解
        
        # 验证关键发现完整度
        assert result["key_findings"] > 0  # 有关键发现
        
        # 验证来源完整度
        assert result["sources"] > 0  # 有来源
        
        # 验证摘要完整度
        assert result["summary"] > 0  # 有摘要
        
        # 验证报告完整度
        assert result["report"] > 0  # 有报告
        
        # 验证总体完整度
        assert result["overall"] > 0  # 总体完整度