"""
测试 ResearchManager 类

测试研究管理器的初始化、获取、保存和删除方法。
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from core.models.research.basic_research import BasicResearch
from core.models.research.research import TopicResearch
from core.models.research.research_manager import ResearchManager


class TestResearchManager:
    """测试 ResearchManager 类"""

    def setup_method(self):
        """测试前设置"""
        # 重置初始化状态
        ResearchManager._initialized = False

    def test_initialize(self):
        """测试初始化"""
        # 调用方法
        ResearchManager.initialize()

        # 验证结果
        assert ResearchManager._initialized is True
        assert ResearchManager._use_db is True

    def test_ensure_initialized(self):
        """测试确保初始化"""
        # 设置未初始化状态
        ResearchManager._initialized = False

        # 调用方法
        ResearchManager.ensure_initialized()

        # 验证结果
        assert ResearchManager._initialized is True

    @patch('core.models.research.research_manager.ResearchManager.get_entity')
    def test_get_research(self, mock_get_entity):
        """测试获取研究报告"""
        # 准备测试数据
        research_id = "research_001"
        mock_research = BasicResearch(
            title="测试研究",
            content_type="test"
        )
        mock_get_entity.return_value = mock_research

        # 调用方法
        result = ResearchManager.get_research(research_id)

        # 验证结果
        assert result == mock_research
        mock_get_entity.assert_called_once_with(research_id)

    @patch('core.models.research.research_manager.ResearchManager.save_entity')
    def test_save_research(self, mock_save_entity):
        """测试保存研究报告"""
        # 准备测试数据
        research = BasicResearch(
            title="测试研究",
            content_type="test"
        )
        mock_save_entity.return_value = True

        # 调用方法
        result = ResearchManager.save_research(research)

        # 验证结果
        assert result is True
        mock_save_entity.assert_called_once_with(research)

    @patch('core.models.research.research_manager.ResearchManager.delete_entity')
    def test_delete_research(self, mock_delete_entity):
        """测试删除研究报告"""
        # 准备测试数据
        research_id = "research_001"
        mock_delete_entity.return_value = True

        # 调用方法
        result = ResearchManager.delete_research(research_id)

        # 验证结果
        assert result is True
        mock_delete_entity.assert_called_once_with(research_id)

    @patch('core.models.research.research_manager.ResearchManager.list_entities')
    def test_list_researches(self, mock_list_entities):
        """测试列出所有研究报告"""
        # 准备测试数据
        mock_ids = ["research_001", "research_002", "research_003"]
        mock_list_entities.return_value = mock_ids

        # 调用方法
        result = ResearchManager.list_researches()

        # 验证结果
        assert result == mock_ids
        mock_list_entities.assert_called_once()

    def test_model_class(self):
        """测试模型类设置"""
        # 验证模型类设置
        assert ResearchManager._model_class == BasicResearch

    def test_id_field(self):
        """测试ID字段设置"""
        # 验证ID字段设置
        assert ResearchManager._id_field == "research_id"

    def test_timestamp_field(self):
        """测试时间戳字段设置"""
        # 验证时间戳字段设置
        assert ResearchManager._timestamp_field == "research_timestamp"

    def test_metadata_field(self):
        """测试元数据字段设置"""
        # 验证元数据字段设置
        assert ResearchManager._metadata_field == "metadata"