"""
测试 ResearchStorage 类

测试临时研究存储的初始化、获取、保存、更新和删除方法。
"""

from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime

from core.models.research.basic_research import BasicResearch, KeyFinding, Source
from core.models.research.research_storage import ResearchStorage
from core.models.infra.temporary_storage import TemporaryStorage


class TestResearchStorage:
    """测试 ResearchStorage 类"""

    def setup_method(self):
        """测试前设置"""
        # 重置存储实例
        ResearchStorage._storage = None

    def test_initialize(self):
        """测试初始化"""
        # 调用方法
        ResearchStorage.initialize()

        # 验证结果
        assert ResearchStorage._storage is not None
        assert isinstance(ResearchStorage._storage, TemporaryStorage)

    @patch('core.models.infra.temporary_storage.TemporaryStorage.get_instance')
    def test_initialize_with_mock(self, mock_get_instance):
        """使用模拟对象测试初始化"""
        # 准备模拟对象
        mock_storage = MagicMock()
        mock_get_instance.return_value = mock_storage

        # 调用方法
        ResearchStorage.initialize()

        # 验证结果
        assert ResearchStorage._storage == mock_storage
        mock_get_instance.assert_called_once_with(
            ResearchStorage._STORAGE_NAME, ResearchStorage._DEFAULT_TTL
        )

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_get_research(self, mock_storage):
        """测试获取研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        mock_research = BasicResearch(
            title="测试临时研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_storage.get.return_value = mock_research

        # 调用方法
        result = ResearchStorage.get_research(research_id)

        # 验证结果
        assert result == mock_research
        mock_storage.get.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_save_research(self, mock_storage):
        """测试保存研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        research = BasicResearch(
            title="测试临时研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_storage.set.return_value = research_id

        # 调用方法
        result = ResearchStorage.save_research(research, research_id)

        # 验证结果
        assert result == research_id
        mock_storage.set.assert_called_once_with(research_id, research)

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_save_research_with_dict(self, mock_storage):
        """测试保存字典形式的研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        research_dict = {
            "title": "测试临时研究",
            "content_type": "article",
            "metadata": {"research_id": research_id},
            "key_findings": []
        }
        mock_storage.set.return_value = research_id

        # 调用方法
        result = ResearchStorage.save_research(research_dict, research_id)

        # 验证结果
        assert result == research_id
        # 验证转换为BasicResearch对象
        mock_storage.set.assert_called_once()
        args, _ = mock_storage.set.call_args
        assert isinstance(args[1], BasicResearch)
        assert args[1].title == "测试临时研究"

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_save_research_without_id(self, mock_storage):
        """测试不提供ID保存研究"""
        # 准备测试数据
        generated_id = "generated_id_001"
        research = BasicResearch(
            title="测试临时研究",
            content_type="article"
        )
        mock_storage.set.return_value = generated_id

        # 调用方法
        result = ResearchStorage.save_research(research)

        # 验证结果
        assert result == generated_id
        mock_storage.set.assert_called_once()
        args, _ = mock_storage.set.call_args
        assert args[0] is None  # 第一个参数应该是None，表示自动生成ID

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_update_research(self, mock_storage):
        """测试更新研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        research = BasicResearch(
            title="更新的临时研究",
            content_type="article",
            metadata={"research_id": research_id}
        )
        mock_storage.update.return_value = True

        # 调用方法
        result = ResearchStorage.update_research(research_id, research)

        # 验证结果
        assert result is True
        mock_storage.update.assert_called_once_with(research_id, research)

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_update_research_with_dict(self, mock_storage):
        """测试更新字典形式的研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        research_dict = {
            "title": "更新的临时研究",
            "content_type": "article",
            "metadata": {"research_id": research_id},
            "key_findings": []
        }
        mock_storage.update.return_value = True

        # 调用方法
        result = ResearchStorage.update_research(research_id, research_dict)

        # 验证结果
        assert result is True
        # 验证转换为BasicResearch对象
        mock_storage.update.assert_called_once()
        args, _ = mock_storage.update.call_args
        assert isinstance(args[1], BasicResearch)
        assert args[1].title == "更新的临时研究"

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_delete_research(self, mock_storage):
        """测试删除研究"""
        # 准备测试数据
        research_id = "temp_research_001"
        mock_storage.delete.return_value = True

        # 调用方法
        result = ResearchStorage.delete_research(research_id)

        # 验证结果
        assert result is True
        mock_storage.delete.assert_called_once_with(research_id)

    @patch('core.models.research.research_storage.ResearchStorage._storage')
    def test_list_researches(self, mock_storage):
        """测试列出所有研究"""
        # 准备测试数据
        mock_ids = ["temp_research_001", "temp_research_002", "temp_research_003"]
        mock_storage.list_keys.return_value = mock_ids

        # 调用方法
        result = ResearchStorage.list_researches()

        # 验证结果
        assert result == mock_ids
        mock_storage.list_keys.assert_called_once()

    def test_storage_name(self):
        """测试存储名称设置"""
        # 验证存储名称设置
        assert ResearchStorage._STORAGE_NAME == "research_storage"

    def test_default_ttl(self):
        """测试默认过期时间设置"""
        # 验证默认过期时间设置
        assert ResearchStorage._DEFAULT_TTL == 24 * 60 * 60  # 24小时