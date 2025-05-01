"""
测试 OutlineAdapter 类

测试大纲适配器的初始化、获取、保存、更新和删除方法。
"""

from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode
from core.models.outline.outline_adapter import OutlineAdapter
from core.models.outline.outline_storage import OutlineStorage


class TestOutlineAdapter:
    """测试 OutlineAdapter 类"""

    @patch('core.models.outline.outline_storage.OutlineStorage.initialize')
    def test_initialize(self, mock_initialize):
        """测试初始化"""
        # 准备测试数据
        mock_initialize.return_value = None

        # 调用方法
        result = OutlineAdapter.initialize()

        # 验证结果
        assert result is True
        mock_initialize.assert_called_once()

    @patch('core.models.outline.outline_storage.OutlineStorage.initialize')
    def test_initialize_with_exception(self, mock_initialize):
        """测试初始化异常处理"""
        # 准备测试数据
        mock_initialize.side_effect = Exception("初始化失败")

        # 调用方法
        result = OutlineAdapter.initialize()

        # 验证结果
        assert result is False
        mock_initialize.assert_called_once()

    @patch('core.models.outline.outline_storage.OutlineStorage.get_outline')
    def test_get_outline(self, mock_get_outline):
        """测试获取大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_get_outline.return_value = mock_outline

        # 调用方法
        result = OutlineAdapter.get_outline(outline_id)

        # 验证结果
        assert result == mock_outline
        mock_get_outline.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.get_outline')
    def test_get_outline_with_exception(self, mock_get_outline):
        """测试获取大纲异常处理"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_get_outline.side_effect = Exception("获取失败")

        # 调用方法
        result = OutlineAdapter.get_outline(outline_id)

        # 验证结果
        assert result is None
        mock_get_outline.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.save_outline')
    def test_save_outline(self, mock_save_outline):
        """测试保存大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_save_outline.return_value = outline_id

        # 调用方法
        result = OutlineAdapter.save_outline(outline, outline_id)

        # 验证结果
        assert result == outline_id
        mock_save_outline.assert_called_once_with(outline, outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.save_outline')
    def test_save_outline_with_exception(self, mock_save_outline):
        """测试保存大纲异常处理"""
        # 准备测试数据
        outline_id = "outline_001"
        outline = BasicOutline(
            title="测试大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_save_outline.side_effect = Exception("保存失败")

        # 调用方法
        result = OutlineAdapter.save_outline(outline, outline_id)

        # 验证结果
        assert result == outline_id
        mock_save_outline.assert_called_once_with(outline, outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.save_outline')
    def test_save_outline_without_id(self, mock_save_outline):
        """测试不提供ID保存大纲"""
        # 准备测试数据
        outline = BasicOutline(
            title="测试大纲",
            content_type="article"
        )
        mock_save_outline.side_effect = Exception("保存失败")

        # 调用方法
        result = OutlineAdapter.save_outline(outline)

        # 验证结果
        assert result == ""
        mock_save_outline.assert_called_once_with(outline, None)

    @patch('core.models.outline.outline_storage.OutlineStorage.update_outline')
    def test_update_outline(self, mock_update_outline):
        """测试更新大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        outline = BasicOutline(
            title="更新的大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_update_outline.return_value = True

        # 调用方法
        result = OutlineAdapter.update_outline(outline_id, outline)

        # 验证结果
        assert result is True
        mock_update_outline.assert_called_once_with(outline_id, outline)

    @patch('core.models.outline.outline_storage.OutlineStorage.update_outline')
    def test_update_outline_with_exception(self, mock_update_outline):
        """测试更新大纲异常处理"""
        # 准备测试数据
        outline_id = "outline_001"
        outline = BasicOutline(
            title="更新的大纲",
            content_type="article",
            metadata={"outline_id": outline_id}
        )
        mock_update_outline.side_effect = Exception("更新失败")

        # 调用方法
        result = OutlineAdapter.update_outline(outline_id, outline)

        # 验证结果
        assert result is False
        mock_update_outline.assert_called_once_with(outline_id, outline)

    @patch('core.models.outline.outline_storage.OutlineStorage.delete_outline')
    def test_delete_outline(self, mock_delete_outline):
        """测试删除大纲"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_delete_outline.return_value = True

        # 调用方法
        result = OutlineAdapter.delete_outline(outline_id)

        # 验证结果
        assert result is True
        mock_delete_outline.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.delete_outline')
    def test_delete_outline_with_exception(self, mock_delete_outline):
        """测试删除大纲异常处理"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_delete_outline.side_effect = Exception("删除失败")

        # 调用方法
        result = OutlineAdapter.delete_outline(outline_id)

        # 验证结果
        assert result is False
        mock_delete_outline.assert_called_once_with(outline_id)

    @patch('core.models.outline.outline_storage.OutlineStorage.list_outlines')
    def test_list_outlines(self, mock_list_outlines):
        """测试列出所有大纲"""
        # 准备测试数据
        mock_ids = ["outline_001", "outline_002", "outline_003"]
        mock_list_outlines.return_value = mock_ids

        # 调用方法
        result = OutlineAdapter.list_outlines()

        # 验证结果
        assert result == mock_ids
        mock_list_outlines.assert_called_once()

    @patch('core.models.outline.outline_storage.OutlineStorage.list_outlines')
    def test_list_outlines_with_exception(self, mock_list_outlines):
        """测试列出所有大纲异常处理"""
        # 准备测试数据
        mock_list_outlines.side_effect = Exception("获取列表失败")

        # 调用方法
        result = OutlineAdapter.list_outlines()

        # 验证结果
        assert result == []
        mock_list_outlines.assert_called_once()