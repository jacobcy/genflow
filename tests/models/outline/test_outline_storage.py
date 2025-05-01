"""
测试 OutlineStorage 类

测试临时大纲存储的初始化、获取、保存、更新和删除方法。
"""

from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode
from core.models.outline.outline_storage import OutlineStorage
from core.models.infra.temporary_storage import TemporaryStorage


class TestOutlineStorage:
    """测试 OutlineStorage 类"""

    def setup_method(self):
        """测试前设置"""
        # 重置存储实例
        OutlineStorage._storage = None

    def test_initialize(self):
        """测试初始化"""
        # 调用方法
        OutlineStorage.initialize()

        # 验证结果
        assert OutlineStorage._storage is not None
        assert isinstance(OutlineStorage._storage, TemporaryStorage)

    @patch('core.models.infra.temporary_storage.TemporaryStorage.get_instance')
    def test_initialize_with_mock(self, mock_get_instance):
        """使用模拟对象测试初始化"""
        # 准备模拟对象
        mock_storage = MagicMock()
        mock_get_instance.return_value = mock_storage

        # 调用方法
        OutlineStorage.initialize()

        # 验证结果
        assert OutlineStorage._storage == mock_storage
        mock_get_instance.assert_called_once_with(
            OutlineStorage._STORAGE_NAME, OutlineStorage._DEFAULT_TTL
        )

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_get_outline(self, mock_storage):
        """测试获取大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        mock_outline = BasicOutline(
            title="测试临时大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_storage.get.return_value = mock_outline

        # 调用方法
        result = OutlineStorage.get_outline(outline_id)

        # 验证结果
        assert result == mock_outline
        mock_storage.get.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_save_outline(self, mock_storage):
        """测试保存大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        outline = BasicOutline(
            title="测试临时大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_storage.set.return_value = outline_id

        # 调用方法
        result = OutlineStorage.save_outline(outline, outline_id)

        # 验证结果
        assert result == outline_id
        mock_storage.set.assert_called_once_with(outline_id, outline)

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_save_outline_with_dict(self, mock_storage):
        """测试保存字典形式的大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        outline_dict = {
            "title": "测试临时大纲",
            "content_type": "article",
            "metadata": {"outline_id": outline_id},
            "nodes": []
        }
        mock_storage.set.return_value = outline_id

        # 调用方法
        result = OutlineStorage.save_outline(outline_dict, outline_id)

        # 验证结果
        assert result == outline_id
        # 验证转换为BasicOutline对象
        mock_storage.set.assert_called_once()
        args, _ = mock_storage.set.call_args
        assert isinstance(args[1], BasicOutline)
        assert args[1].title == "测试临时大纲"

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_save_outline_without_id(self, mock_storage):
        """测试不提供ID保存大纲"""
        # 准备测试数据
        generated_id = "generated_id_001"
        outline = BasicOutline(
            title="测试临时大纲",
            content_type="article"
        )
        mock_storage.set.return_value = generated_id

        # 调用方法
        result = OutlineStorage.save_outline(outline)

        # 验证结果
        assert result == generated_id
        mock_storage.set.assert_called_once()
        args, _ = mock_storage.set.call_args
        assert args[0] is None  # 第一个参数应该是None，表示自动生成ID

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_update_outline(self, mock_storage):
        """测试更新大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        outline = BasicOutline(
            title="更新的临时大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_storage.update.return_value = True

        # 调用方法
        result = OutlineStorage.update_outline(outline_id, outline)

        # 验证结果
        assert result is True
        mock_storage.update.assert_called_once_with(outline_id, outline)

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_update_outline_with_dict(self, mock_storage):
        """测试更新字典形式的大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        outline_dict = {
            "title": "更新的临时大纲",
            "content_type": "article",
            "metadata": {"outline_id": outline_id},
            "nodes": []
        }
        mock_storage.update.return_value = True

        # 调用方法
        result = OutlineStorage.update_outline(outline_id, outline_dict)

        # 验证结果
        assert result is True
        # 验证转换为BasicOutline对象
        mock_storage.update.assert_called_once()
        args, _ = mock_storage.update.call_args
        assert isinstance(args[1], BasicOutline)
        assert args[1].title == "更新的临时大纲"

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_delete_outline(self, mock_storage):
        """测试删除大纲"""
        # 准备测试数据
        outline_id = "temp_outline_001"
        mock_storage.delete.return_value = True

        # 调用方法
        result = OutlineStorage.delete_outline(outline_id)

        # 验证结果
        assert result is True
        mock_storage.delete.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage._storage')
    def test_list_outlines(self, mock_storage):
        """测试列出所有大纲"""
        # 准备测试数据
        mock_ids = ["temp_outline_001", "temp_outline_002", "temp_outline_003"]
        mock_storage.list_keys.return_value = mock_ids

        # 调用方法
        result = OutlineStorage.list_outlines()

        # 验证结果
        assert result == mock_ids
        mock_storage.list_keys.assert_called_once()

    def test_storage_name(self):
        """测试存储名称设置"""
        # 验证存储名称设置
        assert OutlineStorage._STORAGE_NAME == "outline_storage"

    def test_default_ttl(self):
        """测试默认过期时间设置"""
        # 验证默认过期时间设置
        assert OutlineStorage._DEFAULT_TTL == 24 * 60 * 60  # 24小时