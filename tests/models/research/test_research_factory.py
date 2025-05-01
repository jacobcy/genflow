"""
测试 ResearchFactory 类

测试研究工厂的创建、验证和转换方法。
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from core.models.research.basic_research import BasicResearch, Source, ExpertInsight, KeyFinding
from core.models.research.research import TopicResearch
from core.models.research.research_factory import ResearchFactory


class TestResearchFactory:
    """测试 ResearchFactory 类"""

    def test_create_research(self):
        """测试创建研究报告"""
        # 准备测试数据
        title = "测试研究"
        content_type = "test"
        topic_id = "topic_001"
        background = "测试背景"

        # 创建研究报告
        research = ResearchFactory.create_research(
            title=title,
            content_type=content_type,
            topic_id=topic_id,
            background=background
        )

        # 验证结果
        assert isinstance(research, TopicResearch)
        assert research.title == title
        assert research.content_type == content_type
        assert research.topic_id == topic_id
        assert research.background == background
        assert research.id is not None
        assert len(research.id) > 0

    def test_create_research_with_custom_id(self):
        """测试使用自定义ID创建研究报告"""
        # 准备测试数据
        research_id = "custom_id"
        title = "测试研究"
        content_type = "test"

        # 创建研究报告
        research = ResearchFactory.create_research(
            id=research_id,
            title=title,
            content_type=content_type
        )

        # 验证结果
        assert research.id == research_id
        assert research.title == title
        assert research.content_type == content_type

    def test_create_research_with_insights_and_findings(self):
        """测试创建带有见解和发现的研究报告"""
        # 准备测试数据
        title = "测试研究"
        content_type = "test"
        
        # 创建专家见解
        insight = ExpertInsight(
            expert_name="测试专家",
            content="测试内容",
            field="测试领域"
        )
        
        # 创建来源
        source = Source(
            name="测试来源",
            url="https://example.com"
        )
        
        # 创建关键发现
        finding = KeyFinding(
            content="测试发现",
            importance=0.8,
            sources=[source]
        )

        # 创建研究报告
        research = ResearchFactory.create_research(
            title=title,
            content_type=content_type,
            expert_insights=[insight],
            key_findings=[finding],
            sources=[source]
        )

        # 验证结果
        assert research.title == title
        assert research.content_type == content_type
        assert len(research.expert_insights) == 1
        assert research.expert_insights[0].expert_name == "测试专家"
        assert len(research.key_findings) == 1
        assert research.key_findings[0].content == "测试发现"
        assert len(research.sources) == 1
        assert research.sources[0].name == "测试来源"

    @patch('core.models.research.research_factory.ResearchManager')
    def test_get_research(self, mock_manager):
        """测试获取研究报告"""
        # 准备模拟数据
        research_id = "research_001"
        mock_research = TopicResearch(
            id=research_id,
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_manager.get_research.return_value = mock_research
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        result = ResearchFactory.get_research(research_id)

        # 验证结果
        assert result == mock_research
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.get_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_factory.ResearchManager')
    def test_save_research_topic_research(self, mock_manager):
        """测试保存TopicResearch"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_manager.save_research.return_value = True
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        with patch('core.models.research.research_factory.ResearchFactory.validate_research', return_value=True):
            result = ResearchFactory.save_research(research)

        # 验证结果
        assert result == "research_001"
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.save_research.assert_called_once_with(research)

    @patch('core.models.research.research_factory.ResearchManager')
    def test_save_research_basic_research(self, mock_manager):
        """测试保存BasicResearch"""
        # 准备测试数据
        basic_research = BasicResearch(
            title="测试研究",
            content_type="test"
        )
        mock_manager.save_research.return_value = True
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        with patch('core.models.research.research_factory.ResearchFactory.validate_research', return_value=True):
            result = ResearchFactory.save_research(basic_research)

        # 验证结果
        assert isinstance(result, str)
        assert len(result) > 0
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.save_research.assert_called_once()

    @patch('core.models.research.research_factory.ResearchManager')
    def test_save_research_dict(self, mock_manager):
        """测试保存字典形式的研究报告"""
        # 准备测试数据
        research_dict = {
            "id": "research_001",
            "topic_id": "topic_001",
            "title": "测试研究",
            "content_type": "test"
        }
        mock_manager.save_research.return_value = True
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        with patch('core.models.research.research_factory.ResearchFactory.validate_research', return_value=True):
            result = ResearchFactory.save_research(research_dict)

        # 验证结果
        assert result == "research_001"
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.save_research.assert_called_once()

    @patch('core.models.research.research_factory.ResearchManager')
    def test_save_research_invalid(self, mock_manager):
        """测试保存无效的研究报告"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        with patch('core.models.research.research_factory.ResearchFactory.validate_research', return_value=False):
            with pytest.raises(ValueError):
                ResearchFactory.save_research(research)

        # 验证结果
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.save_research.assert_not_called()

    @patch('core.models.research.research_factory.ResearchManager')
    def test_delete_research(self, mock_manager):
        """测试删除研究报告"""
        # 准备测试数据
        research_id = "research_001"
        mock_manager.delete_research.return_value = True
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        result = ResearchFactory.delete_research(research_id)

        # 验证结果
        assert result is True
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.delete_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_factory.ResearchManager')
    def test_list_researches(self, mock_manager):
        """测试列出所有研究报告"""
        # 准备测试数据
        mock_ids = ["research_001", "research_002", "research_003"]
        mock_manager.list_researches.return_value = mock_ids
        mock_manager.ensure_initialized.return_value = None

        # 调用方法
        result = ResearchFactory.list_researches()

        # 验证结果
        assert result == mock_ids
        mock_manager.ensure_initialized.assert_called_once()
        mock_manager.list_researches.assert_called_once()

    def test_create_key_finding(self):
        """测试创建关键发现"""
        # 准备测试数据
        content = "测试发现"
        importance = 0.7
        sources = [{"name": "测试来源", "url": "https://example.com"}]

        # 调用方法
        result = ResearchFactory.create_key_finding(content, importance, sources)

        # 验证结果
        assert isinstance(result, KeyFinding)
        assert result.content == content
        assert result.importance == importance
        assert len(result.sources) == 1
        assert result.sources[0].name == "测试来源"
        assert result.sources[0].url == "https://example.com"

    def test_create_source(self):
        """测试创建来源"""
        # 准备测试数据
        name = "测试来源"
        url = "https://example.com"
        author = "测试作者"
        reliability_score = 0.8
        date = "2023-01-01"

        # 调用方法
        result = ResearchFactory.create_source(name, url, author, reliability_score, date)

        # 验证结果
        assert isinstance(result, Source)
        assert result.name == name
        assert result.url == url
        assert result.author == author
        assert result.reliability_score == reliability_score
        assert result.publish_date == date

    def test_create_expert_insight(self):
        """测试创建专家见解"""
        # 准备测试数据
        expert_name = "测试专家"
        content = "测试内容"
        field = "测试领域"
        credentials = "测试资质"

        # 调用方法
        result = ResearchFactory.create_expert_insight(expert_name, content, field, credentials)

        # 验证结果
        assert isinstance(result, ExpertInsight)
        assert result.expert_name == expert_name
        assert result.content == content
        assert result.field == field
        assert result.credentials == credentials

    def test_from_simple_research(self):
        """测试从简化格式创建研究报告"""
        # 准备测试数据
        title = "测试研究"
        content = "测试内容"
        key_points = [
            {"content": "要点1", "importance": 0.8},
            {"content": "要点2", "importance": 0.6}
        ]
        references = [
            {"title": "参考1", "url": "https://example1.com", "author": "作者1"},
            {"title": "参考2", "url": "https://example2.com", "author": "作者2"}
        ]
        content_type = "test"
        topic_id = "topic_001"

        # 调用方法
        result = ResearchFactory.from_simple_research(
            title=title,
            content=content,
            key_points=key_points,
            references=references,
            content_type=content_type,
            topic_id=topic_id
        )

        # 验证结果
        assert isinstance(result, TopicResearch)
        assert result.title == title
        assert result.content_type == content_type
        assert result.background == content
        assert result.topic_id == topic_id
        assert len(result.key_findings) == 2
        assert result.key_findings[0].content == "要点1"
        assert result.key_findings[0].importance == 0.8
        assert len(result.sources) == 2
        assert result.sources[0].name == "参考1"
        assert result.sources[0].url == "https://example1.com"
        assert result.sources[0].author == "作者1"

    @patch('core.models.research.research_factory.format_research_as_markdown')
    def test_to_markdown(self, mock_formatter):
        """测试转换为Markdown格式"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_formatter.return_value = "# 测试研究\n\n测试内容"

        # 调用方法
        result = ResearchFactory.to_markdown(research)

        # 验证结果
        assert result == "# 测试研究\n\n测试内容"
        mock_formatter.assert_called_once_with(research)

    @patch('core.models.research.research_factory.format_research_as_json')
    def test_to_json(self, mock_formatter):
        """测试转换为JSON格式"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_formatter.return_value = {"id": "research_001", "title": "测试研究"}

        # 调用方法
        result = ResearchFactory.to_json(research)

        # 验证结果
        assert result == {"id": "research_001", "title": "测试研究"}
        mock_formatter.assert_called_once_with(research)

    @patch('core.models.research.research_factory.get_research_completeness')
    def test_get_research_completeness(self, mock_completeness):
        """测试获取研究报告完整度评估"""
        # 准备测试数据
        research = TopicResearch(
            id="research_001",
            topic_id="topic_001",
            title="测试研究",
            content_type="test"
        )
        mock_completeness.return_value = {
            "overall": 75,
            "basic_info": 100,
            "key_findings": 50
        }

        # 调用方法
        result = ResearchFactory.get_research_completeness(research)

        # 验证结果
        assert result == {"overall": 75, "basic_info": 100, "key_findings": 50}
        mock_completeness.assert_called_once_with(research)