"""
测试 Article 数据库操作
"""

import pytest
from unittest.mock import MagicMock

from core.models.article.article import Article
from core.models.article.article_db import ArticleDB


class TestArticleDB:
    """测试 ArticleDB 类"""

    @pytest.fixture
    def mock_db_session(self):
        """提供一个模拟的数据库会话"""
        return MagicMock()

    @pytest.fixture
    def article_db(self, mock_db_session):
        """提供一个 ArticleDB 实例"""
        return ArticleDB(db_session=mock_db_session)

    @pytest.fixture
    def sample_article(self):
        """提供一个示例 Article 对象"""
        return Article(
            id="db_article_001",
            topic_id="db_topic_001",
            title="数据库测试文章",
            content="数据库测试内容",
            content_type="db_test"
        )

    def test_add_article(self, article_db, mock_db_session, sample_article):
        """测试添加文章到数据库"""
        article_db.add_article(sample_article)
        mock_db_session.add.assert_called_once_with(sample_article)
        mock_db_session.commit.assert_called_once()

    def test_get_article_by_id(self, article_db, mock_db_session, sample_article):
        """测试通过 ID 从数据库获取文章"""
        article_id = "db_article_001"
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_article

        retrieved_article = article_db.get_article_by_id(article_id)

        mock_db_session.query.assert_called_once_with(Article)
        # 验证 filter 和 first 被调用
        mock_db_session.query.return_value.filter.return_value.first.assert_called_once()
        assert retrieved_article == sample_article

    def test_get_articles_by_topic_id(self, article_db, mock_db_session, sample_article):
        """测试通过 Topic ID 从数据库获取文章列表"""
        topic_id = "db_topic_001"
        mock_db_session.query.return_value.filter.return_value.all.return_value = [sample_article]

        articles = article_db.get_articles_by_topic_id(topic_id)

        mock_db_session.query.assert_called_once_with(Article)
        # 验证 filter 和 all 被调用
        mock_db_session.query.return_value.filter.return_value.all.assert_called_once()
        assert len(articles) == 1
        assert articles[0] == sample_article

    def test_update_article(self, article_db, mock_db_session, sample_article):
        """测试更新数据库中的文章"""
        # 注意：ArticleDB 通常不直接处理更新逻辑，而是依赖 Session 的状态管理
        # 这里仅测试 commit 是否被调用
        article_db.update_article(sample_article) # 假设有这个方法，或者直接调用 commit
        # 或者更常见的模式是直接调用 session.commit()
        # article_db.db_session.commit()
        mock_db_session.commit.assert_called_once()

    def test_delete_article(self, article_db, mock_db_session, sample_article):
        """测试从数据库删除文章"""
        article_db.delete_article(sample_article)
        mock_db_session.delete.assert_called_once_with(sample_article)
        mock_db_session.commit.assert_called_once()