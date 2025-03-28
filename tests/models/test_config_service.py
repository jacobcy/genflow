"""
测试ConfigService模块

专注测试ConfigService的核心功能，包含配置读取、更新和验证等功能。
只测试关键API，避免测试具体配置项逻辑。
"""

import pytest
from unittest.mock import patch, MagicMock

# 导入被测试模块
from core.models.service.config_service import ConfigService

class TestConfigServiceCore:
    """测试ConfigService的核心功能"""

    @patch('core.models.content_manager.ContentManager')
    def test_is_compatible(self, mock_content_manager):
        """测试内容类型和风格兼容性检查"""
        # 设置模拟行为
        mock_content_manager.is_compatible.return_value = True

        # 调用被测方法
        result = ConfigService.is_compatible("article", "professional")

        # 验证结果
        assert result is True
        mock_content_manager.is_compatible.assert_called_once_with("article", "professional")

    @patch('core.models.content_manager.ContentManager')
    def test_is_compatible_false(self, mock_content_manager):
        """测试内容类型和风格不兼容情况"""
        # 设置模拟行为
        mock_content_manager.is_compatible.return_value = False

        # 调用被测方法
        result = ConfigService.is_compatible("video", "professional")

        # 验证结果
        assert result is False
        mock_content_manager.is_compatible.assert_called_once_with("video", "professional")

    @patch('core.models.content_manager.ContentManager')
    def test_get_recommended_style_for_content_type(self, mock_content_manager):
        """测试获取推荐风格"""
        # 准备模拟数据
        mock_style = MagicMock()

        # 设置模拟行为
        mock_content_manager.get_recommended_style_for_content_type.return_value = mock_style

        # 调用被测方法
        result = ConfigService.get_recommended_style_for_content_type("article")

        # 验证结果
        assert result == mock_style
        mock_content_manager.get_recommended_style_for_content_type.assert_called_once_with("article")

    @patch('core.models.content_manager.ContentManager')
    def test_get_platform_style(self, mock_content_manager):
        """测试获取平台风格"""
        # 准备模拟数据
        mock_style = MagicMock()

        # 设置模拟行为
        mock_content_manager.get_platform_style.return_value = mock_style

        # 调用被测方法
        result = ConfigService.get_platform_style("weibo")

        # 验证结果
        assert result == mock_style
        mock_content_manager.get_platform_style.assert_called_once_with("weibo")

    @patch('core.models.content_manager.ContentManager')
    def test_reload_platform(self, mock_content_manager):
        """测试重新加载平台配置"""
        # 准备模拟数据
        mock_platform = MagicMock()

        # 设置模拟行为
        mock_content_manager.reload_platform.return_value = mock_platform

        # 调用被测方法
        result = ConfigService.reload_platform("weibo")

        # 验证结果
        assert result == mock_platform
        mock_content_manager.reload_platform.assert_called_once_with("weibo")

    @patch('core.models.content_manager.ContentManager')
    def test_reload_all_platforms(self, mock_content_manager):
        """测试重新加载所有平台配置"""
        # 准备模拟数据
        mock_platforms = {
            "weibo": MagicMock(),
            "zhihu": MagicMock()
        }

        # 设置模拟行为
        mock_content_manager.reload_all_platforms.return_value = mock_platforms

        # 调用被测方法
        result = ConfigService.reload_all_platforms()

        # 验证结果
        assert result == mock_platforms
        assert len(result) == 2
        mock_content_manager.reload_all_platforms.assert_called_once()

class TestConfigServiceSyncOperations:
    """测试ConfigService的同步操作功能"""

    @patch('core.models.content_manager.ContentManager')
    def test_sync_configs_to_db(self, mock_content_manager):
        """测试同步配置到数据库"""
        # 设置模拟行为
        mock_content_manager.sync_configs_to_db.return_value = True

        # 调用被测方法
        result = ConfigService.sync_configs_to_db()

        # 验证结果
        assert result is True
        mock_content_manager.sync_configs_to_db.assert_called_once()

    @patch('core.models.content_manager.ContentManager')
    def test_sync_configs_to_db_full(self, mock_content_manager):
        """测试完整同步配置到数据库"""
        # 设置模拟行为
        mock_content_manager.sync_configs_to_db_full.return_value = True

        # 调用被测方法
        result = ConfigService.sync_configs_to_db(full_sync=True)

        # 验证结果
        assert result is True
        mock_content_manager.sync_configs_to_db_full.assert_called_once()

class TestConfigServiceSaveOperations:
    """测试ConfigService的保存操作功能"""

    @patch('core.models.content_manager.ContentManager')
    def test_save_content_type(self, mock_content_manager):
        """测试保存内容类型"""
        # 准备模拟数据
        mock_content_type = MagicMock()

        # 设置模拟行为
        mock_content_manager.save_content_type.return_value = True

        # 调用被测方法
        result = ConfigService.save_content_type(mock_content_type)

        # 验证结果
        assert result is True
        mock_content_manager.save_content_type.assert_called_once_with(mock_content_type)

    @patch('core.models.content_manager.ContentManager')
    def test_save_article_style(self, mock_content_manager):
        """测试保存文章风格"""
        # 准备模拟数据
        mock_style = MagicMock()

        # 设置模拟行为
        mock_content_manager.save_article_style.return_value = True

        # 调用被测方法
        result = ConfigService.save_article_style(mock_style)

        # 验证结果
        assert result is True
        mock_content_manager.save_article_style.assert_called_once_with(mock_style)

    @patch('core.models.content_manager.ContentManager')
    def test_save_platform(self, mock_content_manager):
        """测试保存平台配置"""
        # 准备模拟数据
        mock_platform = MagicMock()

        # 设置模拟行为
        mock_content_manager.save_platform.return_value = True

        # 调用被测方法
        result = ConfigService.save_platform(mock_platform)

        # 验证结果
        assert result is True
        mock_content_manager.save_platform.assert_called_once_with(mock_platform)

    @patch('core.models.content_manager.ContentManager')
    def test_get_content_type_by_category(self, mock_content_manager):
        """测试根据类别获取内容类型"""
        # 准备模拟数据
        mock_content_type = MagicMock()

        # 设置模拟行为
        mock_content_manager.get_content_type_by_category.return_value = mock_content_type

        # 调用被测方法
        result = ConfigService.get_content_type_by_category("文章")

        # 验证结果
        assert result == mock_content_type
        mock_content_manager.get_content_type_by_category.assert_called_once_with("文章")
