"""
测试 SimpleContentManager 类

测试简单内容管理器的初始化和各种临时内容的管理功能。
"""

from unittest.mock import patch, MagicMock
import pytest

from core.models.facade.simple_content_manager import SimpleContentManager
from core.models.research.basic_research import BasicResearch
from core.models.outline.basic_outline import BasicOutline, OutlineNode


class TestSimpleContentManager:
    """测试 SimpleContentManager 类"""

    def setup_method(self):
        """测试前设置"""
        # 重置初始化状态
        SimpleContentManager._initialized = False

    def test_initialize(self):
        """测试初始化"""
        # 模拟依赖的初始化方法
        with patch('core.models.research.research_adapter.ResearchAdapter.initialize') as mock_research_init, \
             patch('core.models.outline.outline_adapter.OutlineAdapter.initialize') as mock_outline_init:

            # 调用方法
            SimpleContentManager.initialize()

            # 验证结果
            assert SimpleContentManager._initialized is True
            mock_research_init.assert_called_once()
            mock_outline_init.assert_called_once()

    def test_ensure_initialized(self):
        """测试确保初始化"""
        # 设置未初始化状态
        SimpleContentManager._initialized = False

        # 模拟初始化方法
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.initialize') as mock_init:
            # 调用方法
            SimpleContentManager.ensure_initialized()

            # 验证结果
            mock_init.assert_called_once()

    #region 基础研究相关测试

    def test_create_basic_research(self):
        """测试创建基础研究对象"""
        # 模拟初始化
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'):
            # 调用方法
            result = SimpleContentManager.create_basic_research(
                title="测试研究",
                content_type="article"
            )

            # 验证结果
            assert isinstance(result, BasicResearch)
            assert result.title == "测试研究"
            assert result.content_type == "article"

    def test_save_basic_research(self):
        """测试保存基础研究对象"""
        # 准备测试数据
        research = BasicResearch(
            title="测试研究",
            content_type="article"
        )
        research_id = "research_001"

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.research.research_adapter.ResearchAdapter.save_research') as mock_save:

            mock_save.return_value = research_id

            # 调用方法
            result = SimpleContentManager.save_basic_research(research, research_id)

            # 验证结果
            assert result == research_id
            mock_save.assert_called_once_with(research, research_id)

    def test_get_basic_research(self):
        """测试获取基础研究对象"""
        # 准备测试数据
        research_id = "research_001"
        mock_research = BasicResearch(
            title="测试研究",
            content_type="article"
        )

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.research.research_adapter.ResearchAdapter.get_research') as mock_get:

            mock_get.return_value = mock_research

            # 调用方法
            result = SimpleContentManager.get_basic_research(research_id)

            # 验证结果
            assert result == mock_research
            mock_get.assert_called_once_with(research_id)

    def test_update_basic_research(self):
        """测试更新基础研究对象"""
        # 准备测试数据
        research_id = "research_001"
        research = BasicResearch(
            title="更新的研究",
            content_type="article"
        )

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.research.research_adapter.ResearchAdapter.update_research') as mock_update:

            mock_update.return_value = True

            # 调用方法
            result = SimpleContentManager.update_basic_research(research_id, research)

            # 验证结果
            assert result is True
            mock_update.assert_called_once_with(research_id, research)

    def test_delete_basic_research(self):
        """测试删除基础研究对象"""
        # 准备测试数据
        research_id = "research_001"

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.research.research_adapter.ResearchAdapter.delete_research') as mock_delete:

            mock_delete.return_value = True

            # 调用方法
            result = SimpleContentManager.delete_basic_research(research_id)

            # 验证结果
            assert result is True
            mock_delete.assert_called_once_with(research_id)

    #endregion

    #region 临时大纲相关测试

    def test_create_basic_outline(self):
        """测试创建基础大纲对象"""
        # 模拟初始化
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'):
            # 调用方法
            result = SimpleContentManager.create_basic_outline(
                title="测试大纲",
                content_type="article"
            )

            # 验证结果
            assert isinstance(result, BasicOutline)
            assert result.title == "测试大纲"
            assert result.content_type == "article"

    def test_save_basic_outline(self):
        """测试保存基础大纲对象"""
        # 准备测试数据
        outline = BasicOutline(
            title="测试大纲",
            content_type="article"
        )
        outline_id = "outline_001"

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.outline.outline_adapter.OutlineAdapter.save_outline') as mock_save:

            mock_save.return_value = outline_id

            # 调用方法
            result = SimpleContentManager.save_basic_outline(outline, outline_id)

            # 验证结果
            assert result == outline_id
            mock_save.assert_called_once_with(outline, outline_id)

    def test_get_basic_outline(self):
        """测试获取基础大纲对象"""
        # 准备测试数据
        outline_id = "outline_001"
        mock_outline = BasicOutline(
            title="测试大纲",
            content_type="article"
        )

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.outline.outline_adapter.OutlineAdapter.get_outline') as mock_get:

            mock_get.return_value = mock_outline

            # 调用方法
            result = SimpleContentManager.get_basic_outline(outline_id)

            # 验证结果
            assert result == mock_outline
            mock_get.assert_called_once_with(outline_id)

    def test_update_basic_outline(self):
        """测试更新基础大纲对象"""
        # 准备测试数据
        outline_id = "outline_001"
        outline = BasicOutline(
            title="更新的大纲",
            content_type="article"
        )

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.outline.outline_adapter.OutlineAdapter.update_outline') as mock_update:

            mock_update.return_value = True

            # 调用方法
            result = SimpleContentManager.update_basic_outline(outline_id, outline)

            # 验证结果
            assert result is True
            mock_update.assert_called_once_with(outline_id, outline)

    def test_delete_basic_outline(self):
        """测试删除基础大纲对象"""
        # 准备测试数据
        outline_id = "outline_001"

        # 模拟依赖
        with patch('core.models.facade.simple_content_manager.SimpleContentManager.ensure_initialized'), \
             patch('core.models.outline.outline_adapter.OutlineAdapter.delete_outline') as mock_delete:

            mock_delete.return_value = True

            # 调用方法
            result = SimpleContentManager.delete_basic_outline(outline_id)

            # 验证结果
            assert result is True
            mock_delete.assert_called_once_with(outline_id)

    #endregion