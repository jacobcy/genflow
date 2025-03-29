"""
GenFlow 核心管理器集成测试

验证ContentManager和各个子管理器之间的协同工作能力，
确保主要功能可通过统一接口正常访问。
"""

import os
import pytest
import shutil
import tempfile
import time
from datetime import datetime

# 导入被测试的模块
from core.models.content_manager import ContentManager
from core.models.infra.config_service import ConfigService
from core.models.infra.db_adapter import DBAdapter

class TestManagerIntegration:
    """测试管理器之间的集成功能"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        # 创建临时目录
        cls.temp_dir = tempfile.mkdtemp()

        # 创建临时配置目录
        cls.config_dir = os.path.join(cls.temp_dir, "config")
        os.makedirs(os.path.join(cls.config_dir, "content_types"), exist_ok=True)
        os.makedirs(os.path.join(cls.config_dir, "styles"), exist_ok=True)
        os.makedirs(os.path.join(cls.config_dir, "platforms"), exist_ok=True)

        # 设置环境配置
        os.environ["GENFLOW_CONFIG_DIR"] = cls.config_dir
        os.environ["GENFLOW_DB_PATH"] = os.path.join(cls.temp_dir, "test_db.sqlite")

        # 初始化管理器
        ConfigService.initialize()
        DBAdapter.initialize()
        ContentManager.initialize()

    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        # 移除临时目录
        shutil.rmtree(cls.temp_dir)

        # 重置环境变量
        if "GENFLOW_CONFIG_DIR" in os.environ:
            del os.environ["GENFLOW_CONFIG_DIR"]
        if "GENFLOW_DB_PATH" in os.environ:
            del os.environ["GENFLOW_DB_PATH"]

    def test_content_flow(self):
        """测试内容流程集成 - 从话题到文章的完整流程"""
        # 1. 创建内容类型
        content_type = {
            "id": "blog",
            "name": "博客文章",
            "description": "标准博客文章格式",
            "format": "long-form",
            "compatible_styles": ["casual", "formal"]
        }
        ContentManager.save_content_type(content_type)

        # 2. 创建文章风格
        article_style = {
            "id": "casual",
            "name": "随性风格",
            "description": "轻松随性的表达方式",
            "tone": "friendly",
            "formality": 2,
            "content_types": ["blog"]
        }
        ContentManager.save_article_style(article_style)

        # 3. 创建话题
        topic_data = {
            "title": "Python编程技巧",
            "description": "介绍Python中有用的编程技巧",
            "keywords": ["Python", "编程", "技巧"],
            "content_type": "blog"
        }
        topic = ContentManager.create_topic(**topic_data)
        assert topic is not None
        assert "id" in topic
        topic_id = topic["id"]

        # 4. 创建大纲
        outline_data = {
            "title": "Python编程技巧大纲",
            "topic_id": topic_id,
            "nodes": [
                {"title": "简介", "content": "关于Python编程的介绍", "level": 1},
                {"title": "基础技巧", "content": "Python基础编程技巧", "level": 1},
                {"title": "高级技巧", "content": "Python高级编程技巧", "level": 1}
            ]
        }
        outline = ContentManager.create_outline(outline_data)
        assert outline is not None
        assert "id" in outline
        outline_id = outline["id"]

        # 5. 创建文章
        article_data = {
            "title": "Python编程技巧精选",
            "content": "这是一篇关于Python编程技巧的文章",
            "topic_id": topic_id,
            "outline_id": outline_id,
            "content_type": "blog",
            "style": "casual"
        }
        article = ContentManager.create_article(article_data)
        assert article is not None
        assert "id" in article
        article_id = article["id"]

        # 6. 验证数据关联
        # 获取话题
        loaded_topic = ContentManager.get_topic(topic_id)
        assert loaded_topic is not None
        assert loaded_topic["id"] == topic_id

        # 获取话题相关大纲
        topic_outlines = ContentManager.get_outlines_by_topic(topic_id)
        assert isinstance(topic_outlines, list)
        assert len(topic_outlines) >= 1
        assert any(o["id"] == outline_id for o in topic_outlines)

        # 获取话题相关文章
        topic_articles = ContentManager.get_articles_by_topic(topic_id)
        assert isinstance(topic_articles, list)
        assert len(topic_articles) >= 1
        assert any(a["id"] == article_id for a in topic_articles)

        # 获取文章详情
        loaded_article = ContentManager.get_article(article_id)
        assert loaded_article is not None
        assert loaded_article["id"] == article_id
        assert loaded_article["topic_id"] == topic_id
        assert loaded_article["outline_id"] == outline_id
        assert loaded_article["content_type"] == "blog"
        assert loaded_article["style"] == "casual"

    def test_config_sync(self):
        """测试配置同步流程"""
        # 创建新的内容类型
        content_type = {
            "id": "news",
            "name": "新闻",
            "description": "新闻文章格式",
            "format": "short-form",
            "compatible_styles": ["formal"]
        }
        ContentManager.save_content_type(content_type)

        # 创建新的风格
        style = {
            "id": "formal",
            "name": "正式风格",
            "description": "正式的表达方式",
            "tone": "professional",
            "formality": 4,
            "content_types": ["news", "blog"]
        }
        ContentManager.save_article_style(style)

        # 验证数据库中有数据
        db_content_type = ContentManager.get_content_type("news")
        assert db_content_type is not None
        assert db_content_type["id"] == "news"

        db_style = ContentManager.get_article_style("formal")
        assert db_style is not None
        assert db_style["id"] == "formal"

        # 导出配置到文件
        DBAdapter.export_content_types_to_config()
        DBAdapter.export_article_styles_to_config()

        # 验证文件存在
        content_type_file = os.path.join(self.config_dir, "content_types", "news.json")
        style_file = os.path.join(self.config_dir, "styles", "formal.json")

        assert os.path.exists(content_type_file)
        assert os.path.exists(style_file)

        # 清除数据库中的数据
        with DBAdapter.get_session() as session:
            session.execute("DELETE FROM content_types WHERE id = 'news'")
            session.execute("DELETE FROM article_styles WHERE id = 'formal'")
            session.commit()

        # 验证数据已清除
        assert ContentManager.get_content_type("news") is None
        assert ContentManager.get_article_style("formal") is None

        # 重新从配置文件导入
        DBAdapter.migrate_content_types_config()
        DBAdapter.migrate_article_styles_config()

        # 验证数据已恢复
        restored_content_type = ContentManager.get_content_type("news")
        assert restored_content_type is not None
        assert restored_content_type["id"] == "news"

        restored_style = ContentManager.get_article_style("formal")
        assert restored_style is not None
        assert restored_style["id"] == "formal"
