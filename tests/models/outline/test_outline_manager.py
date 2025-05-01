"""
测试 OutlineManager 类

测试大纲管理器的初始化、获取、保存和删除方法。
"""

from unittest.mock import patch, MagicMock
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode
from core.models.outline.outline_manager import OutlineManager


class TestOutlineManager:
    """测试 OutlineManager 类"""

    def setup_method(self):
        """测试前设置"""
        # 重置初始化状态
        OutlineManager._initialized = False

    def test_initialize(self):
        """测试初始化"""
        # 调用方法
        OutlineManager.initialize()

        # 验证结果
        assert OutlineManager._initialized is True
        assert OutlineManager._use_db is True

    def test_ensure_initialized(self):
        """测试确保初始化"""
        # 设置未初始化状态
        OutlineManager._initialized = False

        # 调用方法
        OutlineManager.ensure_initialized()

        # 验证结果
        assert OutlineManager._initialized is True

    @patch('core.models.outline.outline_manager.OutlineManager.get_entity')
    def test_get_outline(self, mock_get_entity):
        """测试获取大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_get_entity.return_value = mock_outline

        # 调用方法
        result = OutlineManager.get_outline(outline_id)

        # 验证结果
        assert result == mock_outline
        mock_get_entity.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_manager.OutlineManager.save_entity')
    def test_save_outline(self, mock_save_entity):
        """测试保存大纲"""
        # 准备测试数据
        outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            metadata={"outline_id": "outline_001"}
        )
        mock_save_entity.return_value = True

        # 调用方法
        result = OutlineManager.save_outline(outline)

        # 验证结果
        assert result is True
        mock_save_entity.assert_called_once_with(outline)

    @patch('core.models.outline.outline_manager.OutlineManager.delete_entity')
    def test_delete_outline(self, mock_delete_entity):
        """测试删除大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_delete_entity.return_value = True

        # 调用方法
        result = OutlineManager.delete_outline(outline_id)

        # 验证结果
        assert result is True
        mock_delete_entity.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_manager.OutlineManager.list_entities')
    def test_list_outlines(self, mock_list_entities):
        """测试列出所有大纲"""
        # 准备测试数据
        mock_ids = ["outline_001", "outline_002", "outline_003"]
        mock_list_entities.return_value = mock_ids

        # 调用方法
        result = OutlineManager.list_outlines()

        # 验证结果
        assert result == mock_ids
        mock_list_entities.assert_called_once()

    def test_model_class(self):
        """测试模型类设置"""
        # 验证模型类设置
        assert OutlineManager._model_class == BasicOutline

    def test_id_field(self):
        """测试ID字段设置"""
        # 验证ID字段设置
        assert OutlineManager._id_field == "outline_id"

    def test_metadata_field(self):
        """测试元数据字段设置"""
        # 验证元数据字段设置
        assert OutlineManager._metadata_field == "metadata"

    def test_timestamp_field(self):
        """测试时间戳字段设置"""
        # 验证时间戳字段设置
        assert OutlineManager._timestamp_field == "updated_at"