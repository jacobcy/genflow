"""
测试 TopicResearch 模型

测试标准研究模型的创建、属性和方法。
"""

import pytest
import uuid
from datetime import datetime

from core.models.research.basic_research import BasicResearch, Source, ExpertInsight, KeyFinding
from core.models.research.research import TopicResearch


class TestTopicResearch:
    """测试 TopicResearch 类"""

    def test_create_topic_research(self):
        """测试创建话题研究报告"""
        # 准备测试数据
        research_id = "research_001"
        topic_id = "topic_001"
        title = "Python异步编程最佳实践"
        content_type = "tech_report"
        background = "异步编程是现代应用开发中的重要技术..."

        # 创建话题研究报告
        research = TopicResearch(
            id=research_id,
            topic_id=topic_id,
            title=title,
            content_type=content_type,
            background=background
        )

        # 验证基本属性
        assert research.id == research_id
        assert research.topic_id == topic_id
        assert research.title == title
        assert research.content_type == content_type
        assert research.background == background
        assert isinstance(research.research_timestamp, datetime)
        assert len(research.expert_insights) == 0
        assert len(research.key_findings) == 0
        assert len(research.sources) == 0

    def test_auto_id_generation(self):
        """测试自动生成ID"""
        # 创建话题研究报告，不指定ID
        research = TopicResearch(
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )

        # 验证ID已自动生成
        assert research.id is not None
        assert isinstance(research.id, str)
        assert len(research.id) > 0

    def test_from_basic_research(self):
        """测试从BasicResearch创建TopicResearch"""
        # 创建基础研究
        basic = BasicResearch(
            title="Python测试最佳实践",
            content_type="tutorial",
            background="测试是软件开发的关键环节..."
        )

        # 创建话题研究
        topic_id = "topic_123"
        research_id = "research_123"
        topic_research = TopicResearch.from_basic_research(basic, topic_id, research_id)

        # 验证继承的属性
        assert topic_research.title == basic.title
        assert topic_research.content_type == basic.content_type
        assert topic_research.background == basic.background

        # 验证特有的属性
        assert topic_research.topic_id == topic_id
        assert topic_research.id == research_id

    def test_from_basic_research_auto_id(self):
        """测试从BasicResearch创建TopicResearch时自动生成ID"""
        # 创建基础研究
        basic = BasicResearch(
            title="Python测试最佳实践",
            content_type="tutorial",
            background="测试是软件开发的关键环节..."
        )

        # 创建话题研究，不指定ID
        topic_id = "topic_123"
        topic_research = TopicResearch.from_basic_research(basic, topic_id)

        # 验证ID已自动生成
        assert topic_research.id is not None
        assert isinstance(topic_research.id, str)
        assert len(topic_research.id) > 0
        assert topic_research.topic_id == topic_id

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建话题研究报告
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test",
            background="测试背景",
            summary="测试摘要",
            report="测试报告"
        )

        # 转换为字典
        result = research.to_dict()

        # 验证字典内容
        assert result["id"] == "research_001"
        assert result["topic_id"] == "topic_001"
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