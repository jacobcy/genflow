"""
测试 ArticleFactory
"""

import pytest

from core.models.article.article import Article
from core.models.article.article_factory import ArticleFactory
from core.models.topic.topic import Topic


class TestArticleFactory:
    """测试 ArticleFactory 类"""

    @pytest.fixture
    def sample_topic(self):
        """提供一个示例 Topic 对象"""
        return Topic(id="topic_test_001", title="测试主题")

    def test_create_article_from_topic(self, sample_topic):
        """测试从 Topic 创建 Article"""
        factory = ArticleFactory()
        article_data = {
            "title": "工厂创建的文章标题",
            "content": "工厂创建的文章内容",
            "content_type": "factory_article"
        }
        article = factory.create_article(sample_topic, article_data)

        assert isinstance(article, Article)
        assert article.topic_id == sample_topic.id
        assert article.title == article_data["title"]
        assert article.content == article_data["content"]
        assert article.content_type == article_data["content_type"]
        assert article.id is not None

    def test_create_article_with_id(self, sample_topic):
        """测试创建 Article 时指定 ID"""
        factory = ArticleFactory()
        article_data = {
            "id": "factory_article_002",
            "title": "指定ID的文章",
            "content": "指定ID的内容",
            "content_type": "factory_id_article"
        }
        article = factory.create_article(sample_topic, article_data)

        assert article.id == "factory_article_002"
        assert article.topic_id == sample_topic.id

    def test_create_article_missing_data(self, sample_topic):
        """测试创建 Article 时缺少必要数据"""
        factory = ArticleFactory()
        # 缺少 title
        article_data = {
            "content": "缺少标题的内容",
            "content_type": "missing_data"
        }
        with pytest.raises(KeyError): # 或者根据实际实现可能是 TypeError 或 ValueError
            factory.create_article(sample_topic, article_data)

        # 缺少 content
        article_data_no_content = {
            "title": "缺少内容的标题",
            "content_type": "missing_data"
        }
        with pytest.raises(KeyError): # 同上
            factory.create_article(sample_topic, article_data_no_content)