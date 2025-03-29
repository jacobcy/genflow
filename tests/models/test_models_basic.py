"""
GenFlow 核心模型基本功能测试

该测试集中在核心模型的基本功能上，确保数据存储、加载和基本操作正常工作。
遵循最小可行原则，只测试核心功能，不进行深入的边界测试。
"""

import os
import pytest
import shutil
import tempfile
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

# 导入被测试的模块
from core.models.infra.config_service import ConfigService
from core.models.infra.db_adapter import DBAdapter
from core.models.content_manager import ContentManager

# 测试数据
TEST_CONTENT_TYPE = {
    "id": "test_type",
    "name": "测试内容类型",
    "description": "用于测试的内容类型",
    "format": "article",
    "compatible_styles": ["formal", "casual"]
}

TEST_ARTICLE_STYLE = {
    "id": "test_style",
    "name": "测试风格",
    "description": "用于测试的文章风格",
    "tone": "neutral",
    "formality": 3,
    "content_types": ["test_type"]
}

TEST_PLATFORM = {
    "id": "test_platform",
    "name": "测试平台",
    "description": "用于测试的平台",
    "icon": "test.png",
    "max_length": 5000,
    "min_length": 500
}

TEST_TOPIC = {
    "title": "测试话题",
    "description": "用于测试的话题",
    "keywords": ["测试", "样例"],
    "content_type": "test_type"
}

TEST_OUTLINE = {
    "title": "测试大纲",
    "nodes": [
        {"title": "第一章", "content": "第一章内容", "level": 1},
        {"title": "第二章", "content": "第二章内容", "level": 1}
    ]
}

TEST_ARTICLE = {
    "title": "测试文章",
    "content": "这是一篇测试文章的内容。",
    "content_type": "test_type",
    "style": "test_style"
}


class TestBasicFunctionality:
    """测试核心模型的基本功能"""

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

        # 初始化测试
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

    def test_1_config_service(self):
        """测试配置服务基本功能"""
        # 测试加载配置
        assert ConfigService.get_config_dir() == self.config_dir

        # 测试保存和加载配置
        test_config = {"test": "value", "nested": {"key": "value"}}
        ConfigService.save_config_file("test_config.json", test_config)

        # 测试加载配置
        loaded_config = ConfigService.load_config_file("test_config.json")
        assert loaded_config == test_config

        # 测试点分隔符获取配置
        assert ConfigService.get_config("test_config.test") == "value"
        assert ConfigService.get_config("test_config.nested.key") == "value"

    def test_2_content_types(self):
        """测试内容类型基本功能"""
        # 保存测试内容类型
        ContentManager.save_content_type(TEST_CONTENT_TYPE)

        # 获取内容类型
        content_type = ContentManager.get_content_type(TEST_CONTENT_TYPE["id"])
        assert content_type is not None
        assert content_type["id"] == TEST_CONTENT_TYPE["id"]
        assert content_type["name"] == TEST_CONTENT_TYPE["name"]

        # 获取所有内容类型
        content_types = ContentManager.get_all_content_types()
        assert isinstance(content_types, list)
        assert len(content_types) >= 1
        assert any(ct["id"] == TEST_CONTENT_TYPE["id"] for ct in content_types)

    def test_3_article_styles(self):
        """测试文章风格基本功能"""
        # 保存测试风格
        ContentManager.save_article_style(TEST_ARTICLE_STYLE)

        # 获取风格
        style = ContentManager.get_article_style(TEST_ARTICLE_STYLE["id"])
        assert style is not None
        assert style["id"] == TEST_ARTICLE_STYLE["id"]
        assert style["name"] == TEST_ARTICLE_STYLE["name"]

        # 获取所有风格
        styles = ContentManager.get_all_article_styles()
        assert isinstance(styles, list)
        assert len(styles) >= 1
        assert any(s["id"] == TEST_ARTICLE_STYLE["id"] for s in styles)

        # 测试兼容性检查
        compatibility = ContentManager.check_style_compatibility(
            TEST_ARTICLE_STYLE["id"],
            TEST_CONTENT_TYPE["id"]
        )
        assert compatibility is True

    def test_4_platforms(self):
        """测试平台基本功能"""
        # 保存测试平台
        ContentManager.save_platform(TEST_PLATFORM)

        # 获取平台
        platform = ContentManager.get_platform(TEST_PLATFORM["id"])
        assert platform is not None
        assert platform["id"] == TEST_PLATFORM["id"]
        assert platform["name"] == TEST_PLATFORM["name"]

        # 获取所有平台
        platforms = ContentManager.get_all_platforms()
        assert isinstance(platforms, list)
        assert len(platforms) >= 1
        assert any(p["id"] == TEST_PLATFORM["id"] for p in platforms)

    def test_5_topics(self):
        """测试话题基本功能"""
        # 创建话题
        topic = ContentManager.create_topic(
            title=TEST_TOPIC["title"],
            description=TEST_TOPIC["description"],
            keywords=TEST_TOPIC["keywords"],
            content_type=TEST_TOPIC["content_type"]
        )

        assert topic is not None
        assert "id" in topic
        assert topic["title"] == TEST_TOPIC["title"]

        # 保存话题ID用于后续测试
        self.topic_id = topic["id"]

        # 获取话题
        loaded_topic = ContentManager.get_topic(self.topic_id)
        assert loaded_topic is not None
        assert loaded_topic["id"] == self.topic_id
        assert loaded_topic["title"] == TEST_TOPIC["title"]

    def test_6_outlines(self):
        """测试大纲基本功能"""
        # 创建大纲
        outline_data = {**TEST_OUTLINE, "topic_id": self.topic_id}
        outline = ContentManager.create_outline(outline_data)

        assert outline is not None
        assert "id" in outline
        assert outline["title"] == TEST_OUTLINE["title"]
        assert len(outline["nodes"]) == len(TEST_OUTLINE["nodes"])

        # 保存大纲ID用于后续测试
        self.outline_id = outline["id"]

        # 获取大纲
        loaded_outline = ContentManager.get_outline(self.outline_id)
        assert loaded_outline is not None
        assert loaded_outline["id"] == self.outline_id
        assert loaded_outline["title"] == TEST_OUTLINE["title"]

        # 获取话题相关大纲
        topic_outlines = ContentManager.get_outlines_by_topic(self.topic_id)
        assert isinstance(topic_outlines, list)
        assert len(topic_outlines) >= 1
        assert any(o["id"] == self.outline_id for o in topic_outlines)

    def test_7_articles(self):
        """测试文章基本功能"""
        # 创建文章
        article_data = {
            **TEST_ARTICLE,
            "topic_id": self.topic_id,
            "outline_id": self.outline_id
        }
        article = ContentManager.create_article(article_data)

        assert article is not None
        assert "id" in article
        assert article["title"] == TEST_ARTICLE["title"]

        # 保存文章ID用于后续测试
        self.article_id = article["id"]

        # 获取文章
        loaded_article = ContentManager.get_article(self.article_id)
        assert loaded_article is not None
        assert loaded_article["id"] == self.article_id
        assert loaded_article["title"] == TEST_ARTICLE["title"]

        # 获取话题相关文章
        topic_articles = ContentManager.get_articles_by_topic(self.topic_id)
        assert isinstance(topic_articles, list)
        assert len(topic_articles) >= 1
        assert any(a["id"] == self.article_id for a in topic_articles)

    def test_8_data_syncing(self):
        """测试配置数据同步"""
        # 测试导出配置
        DBAdapter.export_content_types_to_config()
        DBAdapter.export_article_styles_to_config()
        DBAdapter.export_platforms_to_config()

        # 检查配置文件是否生成
        assert os.path.exists(os.path.join(self.config_dir, "content_types", f"{TEST_CONTENT_TYPE['id']}.json"))
        assert os.path.exists(os.path.join(self.config_dir, "styles", f"{TEST_ARTICLE_STYLE['id']}.json"))
        assert os.path.exists(os.path.join(self.config_dir, "platforms", f"{TEST_PLATFORM['id']}.json"))

        # 测试重新导入
        DBAdapter.migrate_content_types_config()
        DBAdapter.migrate_article_styles_config()
        DBAdapter.migrate_platforms_config()

        # 检查数据是否存在
        assert ContentManager.get_content_type(TEST_CONTENT_TYPE["id"]) is not None
        assert ContentManager.get_article_style(TEST_ARTICLE_STYLE["id"]) is not None
        assert ContentManager.get_platform(TEST_PLATFORM["id"]) is not None

    def test_9_basic_error_handling(self):
        """测试基本错误处理"""
        # 测试获取不存在的资源
        assert ContentManager.get_content_type("non_existent") is None
        assert ContentManager.get_article_style("non_existent") is None
        assert ContentManager.get_platform("non_existent") is None
        assert ContentManager.get_topic("non_existent") is None
        assert ContentManager.get_outline("non_existent") is None
        assert ContentManager.get_article("non_existent") is None

        # 测试兼容性检查
        assert ContentManager.check_style_compatibility("non_existent", "non_existent") is False
