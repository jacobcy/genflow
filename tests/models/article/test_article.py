"""
测试 Article 模型
"""

import pytest
from datetime import datetime

from core.models.article.article import Article
from core.models.article.basic_article import BasicArticle


class TestArticle:
    """测试 Article 类"""

    def test_create_article(self):
        """测试创建文章"""
        article = Article(
            id="article_001",
            topic_id="topic_001",
            title="测试文章标题",
            content="测试文章内容",
            content_type="article"
        )
        assert article.id == "article_001"
        assert article.topic_id == "topic_001"
        assert article.title == "测试文章标题"
        assert article.content == "测试文章内容"
        assert article.content_type == "article"
        assert isinstance(article.created_at, datetime)
        assert isinstance(article.updated_at, datetime)

    def test_from_basic_article(self):
        """测试从 BasicArticle 创建 Article"""
        basic = BasicArticle(
            title="基础文章标题",
            content="基础文章内容",
            content_type="basic"
        )
        article = Article(
            id="article_002",
            topic_id="topic_002",
            title=basic.title,
            content=basic.content,
            content_type=basic.content_type
        )
        assert article.id == "article_002"
        assert article.topic_id == "topic_002"
        assert article.title == basic.title
        assert article.content == basic.content
        assert article.content_type == basic.content_type

    def test_to_dict(self):
        """测试转换为字典"""
        article = Article(
            id="article_001",
            topic_id="topic_001",
            title="测试文章标题",
            content="测试文章内容",
            content_type="article"
        )
        data = article.to_dict()
        assert data["id"] == "article_001"
        assert data["topic_id"] == "topic_001"
        assert data["title"] == "测试文章标题"
        assert data["content"] == "测试文章内容"
        assert data["content_type"] == "article"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "id": "article_003",
            "topic_id": "topic_003",
            "title": "字典文章标题",
            "content": "字典文章内容",
            "content_type": "dict_article",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        article = Article.from_dict(data)
        assert article.id == "article_003"
        assert article.topic_id == "topic_003"
        assert article.title == "字典文章标题"
        assert article.content == "字典文章内容"
        assert article.content_type == "dict_article"
        assert isinstance(article.created_at, datetime)
        assert isinstance(article.updated_at, datetime)