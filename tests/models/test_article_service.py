"""
测试ArticleService模块

专注测试ArticleService的核心功能，包括文章验证、平台准备、风格应用等操作。
不测试全流程生成逻辑，专注于独立功能点。
"""

import pytest
from unittest.mock import patch, MagicMock

# 导入被测试模块
from core.models.service.article_service import ArticleService
from core.models.article import Article
from core.models.platform import Platform

class TestArticleServiceStyles:
    """测试ArticleService的风格相关功能"""

    def test_apply_style(self):
        """测试应用文章风格"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.style_id = None
        mock_style = MagicMock()
        mock_style.id = "professional"

        # 调用被测方法
        result = ArticleService.apply_style(mock_article, mock_style)

        # 验证结果
        assert result is True
        assert mock_article.style_id == "professional"
        mock_article.update_status.assert_called_once_with("style")

    def test_apply_style_exception(self):
        """测试应用文章风格异常情况"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.update_status.side_effect = Exception("测试异常")
        mock_style = MagicMock()

        # 调用被测方法
        result = ArticleService.apply_style(mock_article, mock_style)

        # 验证结果
        assert result is False

class TestArticleServicePlatform:
    """测试ArticleService的平台相关功能"""

    @patch('core.models.article_service.get_default_platform')
    def test_validate_for_platform_no_platform_specified(self, mock_get_default_platform):
        """测试在未指定平台时验证文章"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.platform_id = None
        mock_article.calculate_metrics.return_value = {
            "word_count": 1000,
            "image_count": 2
        }

        mock_platform = MagicMock()
        mock_platform.validate_content.return_value = {
            "title_length_check": True,
            "content_length_check": True,
            "image_count_check": True
        }
        mock_platform.constraints.forbidden_words = ["敏感词"]
        mock_platform.get_platform_constraints.return_value = {"max_length": 2000}

        mock_get_default_platform.return_value = mock_platform

        # 调用被测方法
        result = ArticleService.validate_for_platform(mock_article)

        # 验证结果
        assert result["is_valid"] is True
        assert result["validation_details"]["forbidden_words_check"] is True
        assert result["platform_constraints"] == {"max_length": 2000}
        mock_article.calculate_metrics.assert_called_once()
        mock_platform.validate_content.assert_called_once()

    @patch('core.models.platform.PLATFORM_CONFIGS')
    def test_validate_for_platform_with_forbidden_words(self, mock_platform_configs):
        """测试包含禁用词的文章验证"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.platform_id = "weibo"
        mock_article.title = "测试包含敏感词的标题"
        mock_article.summary = "测试摘要"
        mock_article.sections = [
            MagicMock(content="正常内容"),
            MagicMock(content="包含敏感词的内容")
        ]
        mock_article.calculate_metrics.return_value = {
            "word_count": 1000,
            "image_count": 2
        }

        mock_platform = MagicMock()
        mock_platform.validate_content.return_value = {
            "title_length_check": True,
            "content_length_check": True,
            "image_count_check": True
        }
        mock_platform.constraints.forbidden_words = ["敏感词"]
        mock_platform.get_platform_constraints.return_value = {"max_length": 2000}

        mock_platform_configs.get.return_value = mock_platform

        # 调用被测方法
        result = ArticleService.validate_for_platform(mock_article, mock_platform)

        # 验证结果
        assert result["is_valid"] is False
        assert result["validation_details"]["forbidden_words_check"] is False
        assert "敏感词" in result["forbidden_words_found"]

    @patch('core.models.platform.PLATFORM_CONFIGS')
    def test_prepare_for_platform_valid(self, mock_platform_configs):
        """测试为平台准备符合要求的文章"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.calculate_metrics.return_value = {
            "word_count": 1000,
            "image_count": 2
        }

        mock_platform = MagicMock()
        mock_platform.name = "微博"
        mock_platform.validate_content.return_value = {
            "title_length_check": True,
            "content_length_check": True,
            "image_count_check": True
        }
        mock_platform.constraints.forbidden_words = []
        mock_platform.get_platform_constraints.return_value = {"max_length": 2000}

        mock_platform_configs.get.return_value = mock_platform

        # 调用被测方法
        result = ArticleService.prepare_for_platform(mock_article, "weibo")

        # 验证结果
        assert result["is_valid"] is True
        assert result["platform"] == "微博"
        assert result["needs_manual_review"] is False
        assert mock_article.platform_id == "weibo"
        mock_article.update_status.assert_called_once_with("review")

class TestArticleServiceGeneral:
    """测试ArticleService的通用功能"""

    @patch('core.models.article_service.ContentType')
    def test_get_content_type_instance(self, mock_content_type_class):
        """测试获取内容类型实例"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.content_type = "blog"

        mock_content_type = MagicMock()
        mock_content_type_class.from_name.return_value = mock_content_type

        # 调用被测方法
        result = ArticleService.get_content_type_instance(mock_article)

        # 验证结果
        assert result == mock_content_type
        mock_content_type_class.from_name.assert_called_once_with("blog")

    @patch('core.models.article_service.ContentType')
    def test_get_content_type_instance_not_found(self, mock_content_type_class):
        """测试获取不存在的内容类型"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.content_type = "nonexistent"

        mock_content_type_class.from_name.side_effect = ValueError("Content type not found")

        # 调用被测方法
        result = ArticleService.get_content_type_instance(mock_article)

        # 验证结果
        assert result is None
        mock_content_type_class.from_name.assert_called_once_with("nonexistent")

    @patch('core.models.article_service.Topic')
    def test_get_topic(self, mock_topic_class):
        """测试获取关联话题"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.topic_id = "topic123"

        mock_topic = MagicMock()
        mock_topic_class.from_id.return_value = mock_topic

        # 调用被测方法
        result = ArticleService.get_topic(mock_article)

        # 验证结果
        assert result == mock_topic
        mock_topic_class.from_id.assert_called_once_with("topic123")

    @patch('core.models.content_manager.ContentManager')
    def test_save_article(self, mock_content_manager):
        """测试保存文章"""
        # 准备模拟数据
        mock_article = MagicMock()

        # 设置模拟行为
        mock_content_manager.save_article.return_value = True

        # 调用被测方法
        result = ArticleService.save_article(mock_article)

        # 验证结果
        assert result is True
        mock_content_manager.save_article.assert_called_once_with(mock_article)

    @patch('core.models.content_manager.ContentManager')
    def test_save_article_failure(self, mock_content_manager):
        """测试保存文章失败"""
        # 准备模拟数据
        mock_article = MagicMock()

        # 设置模拟行为
        mock_content_manager.save_article.side_effect = Exception("保存失败")

        # 调用被测方法
        result = ArticleService.save_article(mock_article)

        # 验证结果
        assert result is False
        mock_content_manager.save_article.assert_called_once_with(mock_article)

    def test_update_article_status(self):
        """测试更新文章状态"""
        # 准备模拟数据
        mock_article = MagicMock()

        # 模拟ArticleService.save_article方法
        with patch.object(ArticleService, 'save_article', return_value=True):
            # 调用被测方法
            result = ArticleService.update_article_status(mock_article, "published")

            # 验证结果
            assert result is True
            mock_article.update_status.assert_called_once_with("published")
            ArticleService.save_article.assert_called_once_with(mock_article)

    def test_update_article_status_failure(self):
        """测试更新文章状态失败"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.update_status.side_effect = Exception("状态更新失败")

        # 调用被测方法
        result = ArticleService.update_article_status(mock_article, "published")

        # 验证结果
        assert result is False
