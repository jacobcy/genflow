"""
测试 ArticleManager
"""

import pytest
from unittest.mock import MagicMock

from core.models.article.article import Article
from core.models.article.article_manager import ArticleManager
from core.models.topic.topic import Topic


class TestArticleManager:
    """测试 ArticleManager 类"""

    @pytest.fixture
    def mock_db_session(self):
        """提供一个模拟的数据库会话"""
        return MagicMock()

    @pytest.fixture
    def mock_article_factory(self):
        """提供一个模拟的 ArticleFactory"""
        return MagicMock()

    @pytest.fixture
    def article_manager(self, mock_db_session, mock_article_factory):
        """提供一个 ArticleManager 实例"""
        return ArticleManager(db_session=mock_db_session, article_factory=mock_article_factory)

    @pytest.fixture
    def sample_topic(self):
        """提供一个示例 Topic 对象"""
        return Topic(id="topic_mngr_001", title="管理器测试主题")

    @pytest.fixture
    def sample_article_data(self):
        """提供示例文章数据"""
        return {
            "title": "管理器创建的文章",
            "content": "管理器创建的内容",
            "content_type": "manager_article"
        }

    @pytest.fixture
    def sample_article(self, sample_topic, sample_article_data):
        """提供一个示例 Article 对象"""
        return Article(
            id="mngr_article_001",
            topic_id=sample_topic.id,
            **sample_article_data
        )

    def test_create_article(self, article_manager, mock_article_factory, mock_db_session, sample_topic, sample_article_data, sample_article):
        """测试创建文章"""
        # 配置模拟工厂返回示例文章
        mock_article_factory.create_article.return_value = sample_article

        # 调用创建方法
        created_article = article_manager.create_article(sample_topic, sample_article_data)

        # 验证工厂被正确调用
        mock_article_factory.create_article.assert_called_once_with(sample_topic, sample_article_data)
        # 验证数据库会话添加和提交被调用
        mock_db_session.add.assert_called_once_with(sample_article)
        mock_db_session.commit.assert_called_once()
        # 验证返回的文章是工厂创建的文章
        assert created_article == sample_article

    def test_get_article_by_id(self, article_manager, mock_db_session, sample_article):
        """测试通过 ID 获取文章"""
        article_id = "mngr_article_001"
        # 配置模拟数据库查询返回示例文章
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_article

        # 调用获取方法
        retrieved_article = article_manager.get_article_by_id(article_id)

        # 验证数据库查询被正确调用
        mock_db_session.query.assert_called_once_with(Article)
        # 可以在这里添加更详细的 filter 调用断言，但这通常比较复杂
        # mock_db_session.query.return_value.filter.assert_called_once_with(Article.id == article_id)
        mock_db_session.query.return_value.filter.return_value.first.assert_called_once()
        # 验证返回的文章是模拟数据库返回的文章
        assert retrieved_article == sample_article

    def test_get_articles_by_topic_id(self, article_manager, mock_db_session, sample_article):
        """测试通过 Topic ID 获取文章列表"""
        topic_id = "topic_mngr_001"
        # 配置模拟数据库查询返回包含示例文章的列表
        mock_db_session.query.return_value.filter.return_value.all.return_value = [sample_article]

        # 调用获取方法
        articles = article_manager.get_articles_by_topic_id(topic_id)

        # 验证数据库查询被正确调用
        mock_db_session.query.assert_called_once_with(Article)
        # mock_db_session.query.return_value.filter.assert_called_once_with(Article.topic_id == topic_id)
        mock_db_session.query.return_value.filter.return_value.all.assert_called_once()
        # 验证返回的文章列表
        assert len(articles) == 1
        assert articles[0] == sample_article

    def test_update_article(self, article_manager, mock_db_session, sample_article):
        """测试更新文章"""
        update_data = {"title": "更新后的标题", "content": "更新后的内容"}

        # 调用更新方法
        updated_article = article_manager.update_article(sample_article, update_data)

        # 验证文章属性被更新
        assert updated_article.title == update_data["title"]
        assert updated_article.content == update_data["content"]
        # 验证数据库提交被调用
        mock_db_session.commit.assert_called_once()
        # 验证返回更新后的文章
        assert updated_article == sample_article # 因为是原地修改

    def test_delete_article(self, article_manager, mock_db_session, sample_article):
        """测试删除文章"""
        # 调用删除方法
        article_manager.delete_article(sample_article)

        # 验证数据库删除和提交被调用
        mock_db_session.delete.assert_called_once_with(sample_article)
        mock_db_session.commit.assert_called_once()