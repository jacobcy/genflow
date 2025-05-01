"""
测试 ResearchAdapter 类

测试研究适配器的初始化、获取、保存、更新和删除方法。
"""

from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime

from core.models.research.basic_research import BasicResearch, KeyFinding, Source
from core.models.research.research_adapter import ResearchAdapter
from core.models.research.research_storage import ResearchStorage


class TestResearchAdapter:
    """测试 ResearchAdapter 类"""

    @patch('core.models.research.research_storage.ResearchStorage.initialize')
    def test_initialize(self, mock_initialize):
        """测试初始化"""
        # 准备测试数据
        mock_initialize.return_value = None

        # 调用方法
        result = ResearchAdapter.initialize()

        # 验证结果
        assert result is True
        mock_initialize.assert_called_once()

    @patch('core.models.research.research_storage.ResearchStorage.initialize')
    def test_initialize_with_exception(self, mock_initialize):
        """测试初始化异常处理"""
        # 准备测试数据
        mock_initialize.side_effect = Exception("初始化失败")

        # 调用方法
        result = ResearchAdapter.initialize()

        # 验证结果
        assert result is False
        mock_initialize.assert_called_once()

    @patch('core.models.research.research_storage.ResearchStorage.get_research')
    def test_get_research(self, mock_get_research):
        """测试获取研究"""
        # 准备测试数据
        research_id = "research_001"
        mock_research = BasicResearch(
            title="测试研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_get_research.return_value = mock_research

        # 调用方法
        result = ResearchAdapter.get_research(research_id)

        # 验证结果
        assert result == mock_research
        mock_get_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage.get_research')
    def test_get_research_with_exception(self, mock_get_research):
        """测试获取研究异常处理"""
        # 准备测试数据
        research_id = "research_001"
        mock_get_research.side_effect = Exception("获取失败")

        # 调用方法
        result = ResearchAdapter.get_research(research_id)

        # 验证结果
        assert result is None
        mock_get_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage.save_research')
    def test_save_research(self, mock_save_research):
        """测试保存研究"""
        # 准备测试数据
        research_id = "research_001"
        research = BasicResearch(
            title="测试研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_save_research.return_value = research_id

        # 调用方法
        result = ResearchAdapter.save_research(research, research_id)

        # 验证结果
        assert result == research_id
        mock_save_research.assert_called_once_with(research, research_id)

    @patch('core.models.research.research_storage.ResearchStorage.save_research')
    def test_save_research_with_exception(self, mock_save_research):
        """测试保存研究异常处理"""
        # 准备测试数据
        research_id = "research_001"
        research = BasicResearch(
            title="测试研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_save_research.side_effect = Exception("保存失败")

        # 调用方法
        result = ResearchAdapter.save_research(research, research_id)

        # 验证结果
        assert result == research_id
        mock_save_research.assert_called_once_with(research, research_id)

    @patch('core.models.research.research_storage.ResearchStorage.save_research')
    def test_save_research_without_id(self, mock_save_research):
        """测试不提供ID保存研究"""
        # 准备测试数据
        research = BasicResearch(
            title="测试研究",
            content_type="article"
        )
        mock_save_research.side_effect = Exception("保存失败")

        # 调用方法
        result = ResearchAdapter.save_research(research)

        # 验证结果
        assert result == ""
        mock_save_research.assert_called_once_with(research, None)

    @patch('core.models.research.research_storage.ResearchStorage.update_research')
    def test_update_research(self, mock_update_research):
        """测试更新研究"""
        # 准备测试数据
        research_id = "research_001"
        research = BasicResearch(
            title="更新的研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_update_research.return_value = True

        # 调用方法
        result = ResearchAdapter.update_research(research_id, research)

        # 验证结果
        assert result is True
        mock_update_research.assert_called_once_with(research_id, research)

    @patch('core.models.research.research_storage.ResearchStorage.update_research')
    def test_update_research_with_exception(self, mock_update_research):
        """测试更新研究异常处理"""
        # 准备测试数据
        research_id = "research_001"
        research = BasicResearch(
            title="更新的研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_update_research.side_effect = Exception("更新失败")

        # 调用方法
        result = ResearchAdapter.update_research(research_id, research)

        # 验证结果
        assert result is False
        mock_update_research.assert_called_once_with(research_id, research)

    @patch('core.models.research.research_storage.ResearchStorage.delete_research')
    def test_delete_research(self, mock_delete_research):
        """测试删除研究"""
        # 准备测试数据
        research_id = "research_001"
        mock_delete_research.return_value = True

        # 调用方法
        result = ResearchAdapter.delete_research(research_id)

        # 验证结果
        assert result is True
        mock_delete_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage.delete_research')
    def test_delete_research_with_exception(self, mock_delete_research):
        """测试删除研究异常处理"""
        # 准备测试数据
        research_id = "research_001"
        mock_delete_research.side_effect = Exception("删除失败")

        # 调用方法
        result = ResearchAdapter.delete_research(research_id)

        # 验证结果
        assert result is False
        mock_delete_research.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage.list_researches')
    def test_list_researches(self, mock_list_researches):
        """测试列出所有研究"""
        # 准备测试数据
        mock_ids = ["research_001", "research_002", "research_003"]
        mock_list_researches.return_value = mock_ids

        # 调用方法
        result = ResearchAdapter.list_researches()

        # 验证结果
        assert result == mock_ids
        mock_list_researches.assert_called_once()

    @patch('core.models.research.research_storage.ResearchStorage.list_researches')
    def test_list_researches_with_exception(self, mock_list_researches):
        """测试列出所有研究异常处理"""
        # 准备测试数据
        mock_list_researches.side_effect = Exception("获取列表失败")

        # 调用方法
        result = ResearchAdapter.list_researches()

        # 验证结果
        assert result == []
        mock_list_researches.assert_called_once()