"""
测试 BasicArticle 模型
"""

import pytest
from datetime import datetime

from core.models.article.basic_article import BasicArticle


class TestBasicArticle:
    """测试 BasicArticle 类"""

    def test_create_basic_article(self):
        """测试创建基础文章"""
        article = BasicArticle(
            title="测试标题",
            content="测试内容",
            content_type="test"
        )
        assert article.title == "测试标题"
        assert article.content == "测试内容"
        assert article.content_type == "test"
        assert isinstance(article.created_at, datetime)
        assert isinstance(article.updated_at, datetime)
        assert article.id is not None

    def test_to_dict(self):
        """测试转换为字典"""
        article = BasicArticle(
            id="basic_001",
            title="测试标题",
            content="测试内容",
            content_type="test"
        )
        data = article.to_dict()
        assert data["id"] == "basic_001"
        assert data["title"] == "测试标题"
        assert data["content"] == "测试内容"
        assert data["content_type"] == "test"
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "id": "basic_002",
            "title": "字典标题",
            "content": "字典内容",
            "content_type": "dict_test",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        article = BasicArticle.from_dict(data)
        assert article.id == "basic_002"
        assert article.title == "字典标题"
        assert article.content == "字典内容"
        assert article.content_type == "dict_test"
        assert isinstance(article.created_at, datetime)
        assert isinstance(article.updated_at, datetime)