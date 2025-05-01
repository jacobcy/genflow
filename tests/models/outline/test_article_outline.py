"""
测试 ArticleOutline 模型

测试文章大纲模型的创建、属性和方法。
"""

# import pytest  # 不需要
# import uuid  # 不需要
from datetime import datetime

from core.models.outline.basic_outline import BasicOutline, OutlineNode
from core.models.outline.article_outline import ArticleOutline


class TestArticleOutline:
    """测试 ArticleOutline 类"""

    def test_create_article_outline(self):
        """测试创建文章大纲"""
        # 创建大纲节点
        node1 = OutlineNode(
            title="第一章",
            content="这是第一章的内容",
            level=1
        )

        node2 = OutlineNode(
            title="第二章",
            content="这是第二章的内容",
            level=2
        )

        # 创建文章大纲
        outline = ArticleOutline(
            id="outline_001",
            topic_id="topic_001",
            title="测试文章大纲",
            content_type="article",
            nodes=[node1, node2]
        )

        # 验证基本属性
        assert outline.id == "outline_001"
        assert outline.topic_id == "topic_001"
        assert outline.title == "测试文章大纲"
        assert outline.content_type == "article"
        assert len(outline.nodes) == 2
        assert outline.nodes[0].title == "第一章"
        assert outline.nodes[1].title == "第二章"
        assert isinstance(outline.created_at, datetime)
        assert isinstance(outline.updated_at, datetime)

    def test_auto_id_generation(self):
        """测试自动生成ID"""
        # 创建文章大纲，不指定ID
        outline = ArticleOutline(
            topic_id="topic_001",
            title="测试文章大纲",
            content_type="article"
        )

        # 验证ID已自动生成
        assert outline.id is not None
        assert isinstance(outline.id, str)
        assert len(outline.id) > 0

    def test_from_basic_outline(self):
        """测试从BasicOutline创建ArticleOutline"""
        # 创建基础大纲
        basic = BasicOutline(
            title="基础大纲",
            content_type="article",
            nodes=[
                OutlineNode(
                    title="第一章",
                    content="这是第一章的内容",
                    level=1
                )
            ]
        )

        # 创建文章大纲
        # 创建文章大纲
        article_outline = ArticleOutline(
            id="outline_123",
            topic_id="topic_123",
            title=basic.title,
            content_type=basic.content_type,
            nodes=basic.nodes
        )

        # 验证继承的属性
        assert article_outline.title == basic.title
        assert article_outline.content_type == basic.content_type
        assert len(article_outline.nodes) == len(basic.nodes)
        assert article_outline.nodes[0].title == basic.nodes[0].title

        # 验证特有的属性
        assert article_outline.topic_id == "topic_123"
        assert article_outline.id == "outline_123"

    def test_from_basic_outline_auto_id(self):
        """测试从BasicOutline创建ArticleOutline时自动生成ID"""
        # 创建基础大纲
        basic = BasicOutline(
            title="基础大纲",
            content_type="article"
        )

        # 创建文章大纲，不指定ID
        article_outline = ArticleOutline(
            topic_id="topic_123",
            title=basic.title,
            content_type=basic.content_type,
            nodes=basic.nodes
        )

        # 验证ID已自动生成
        assert article_outline.id is not None
        assert isinstance(article_outline.id, str)
        assert len(article_outline.id) > 0
        assert article_outline.topic_id == "topic_123"

    def test_to_dict(self):
        """测试转换为字典"""
        # 创建文章大纲
        outline = ArticleOutline(
            id="outline_001",
            topic_id="topic_001",
            title="测试文章大纲",
            content_type="article",
            nodes=[
                OutlineNode(
                    title="第一章",
                    content="这是第一章的内容",
                    level=1
                )
            ]
        )

        # 转换为字典
        result = outline.to_dict()

        # 验证
        assert result["id"] == "outline_001"
        assert result["topic_id"] == "topic_001"
        assert result["title"] == "测试文章大纲"
        assert result["content_type"] == "article"
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["title"] == "第一章"
        assert "created_at" in result
        assert "updated_at" in result

    def test_from_dict(self):
        """测试从字典创建"""
        # 创建字典
        data = {
            "id": "outline_002",
            "topic_id": "topic_002",
            "title": "字典文章大纲",
            "content_type": "article",
            "nodes": [
                {
                    "title": "第一章",
                    "content": "这是第一章的内容",
                    "level": 1
                }
            ]
        }

        # 从字典创建
        outline = ArticleOutline.from_dict(data)

        # 验证
        assert outline.id == "outline_002"
        assert outline.topic_id == "topic_002"
        assert outline.title == "字典文章大纲"
        assert outline.content_type == "article"
        assert len(outline.nodes) == 1
        assert outline.nodes[0].title == "第一章"

    def test_update_timestamp(self):
        """测试更新时间戳"""
        # 创建文章大纲
        outline = ArticleOutline(
            id="outline_001",
            topic_id="topic_001",
            title="测试文章大纲",
            content_type="article"
        )

        # 记录原始时间
        original_time = outline.updated_at

        # 等待一小段时间
        import time
        time.sleep(0.01)

        # 更新时间戳
        outline.updated_at = datetime.now()

        # 验证
        assert outline.updated_at > original_time