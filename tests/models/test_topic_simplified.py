"""
测试Topic模型（简化版）

专注测试Topic模型的核心功能，包括创建、基本属性和序列化，
移除了热度和趋势相关的测试，符合最小可行产品原则。
"""

import pytest
import uuid
from datetime import datetime

# 导入被测试模块
from core.models.topic.topic import Topic

class TestTopicBasics:
    """测试Topic基本功能"""

    def test_create_topic(self):
        """测试创建基本话题"""
        # 创建话题实例
        topic = Topic(
            id="test_id",
            title="测试话题",
            description="这是一个测试话题",
            content_type="article",
            keywords=["测试", "样例"],
            language="zh-CN"
        )

        # 验证属性
        assert topic.id == "test_id"
        assert topic.title == "测试话题"
        assert topic.description == "这是一个测试话题"
        assert topic.content_type == "article"
        assert "测试" in topic.keywords
        assert "样例" in topic.keywords
        assert topic.language == "zh-CN"

    def test_create_minimal_topic(self):
        """测试创建最小话题"""
        # 创建话题实例，只提供必要字段
        topic = Topic(
            title="测试话题"
        )

        # 验证属性
        assert topic.title == "测试话题"
        assert topic.id is not None  # 应自动生成ID
        assert isinstance(topic.id, str)
        assert topic.description == ""  # 默认值
        assert topic.keywords == []  # 默认值
        assert topic.language == "zh-CN"  # 默认值

    def test_auto_id_generation(self):
        """测试自动生成ID"""
        # 创建话题实例，不指定ID
        topic = Topic(
            title="测试话题"
        )

        # 验证ID格式
        assert isinstance(topic.id, str)
        assert len(topic.id) > 0

class TestTopicSerialization:
    """测试Topic序列化功能"""

    def test_to_dict(self):
        """测试话题转换为字典"""
        # 创建当前时间
        now = datetime.now()

        # 创建话题实例
        topic = Topic(
            id="test_id",
            title="测试话题",
            description="这是一个测试话题",
            content_type="article",
            keywords=["测试", "样例"],
            language="zh-CN",
            created_at=now,
            updated_at=now
        )

        # 调用to_dict方法
        result = topic.to_dict()

        # 验证结果
        assert result["id"] == "test_id"
        assert result["title"] == "测试话题"
        assert result["description"] == "这是一个测试话题"
        assert result["content_type"] == "article"
        assert result["keywords"] == ["测试", "样例"]
        assert result["language"] == "zh-CN"

        # 验证时间字段
        assert "created_at" in result
        assert "updated_at" in result

    def test_to_json(self):
        """测试话题转换为JSON"""
        # 创建话题实例
        topic = Topic(
            id="test_id",
            title="测试话题"
        )

        # 调用to_json方法
        json_data = topic.to_json()

        # 验证结果
        assert isinstance(json_data, str)
        assert "test_id" in json_data
        assert "测试话题" in json_data

class TestTopicValidation:
    """测试Topic数据验证功能"""

    def test_validate_title(self):
        """测试标题验证"""
        # 空标题
        with pytest.raises(ValueError):
            Topic(title="")

        # 标题过长
        with pytest.raises(ValueError):
            Topic(title="x" * 201)  # 201个字符，超过200的限制

    def test_update_timestamp(self):
        """测试更新时间戳"""
        # 创建话题实例
        topic = Topic(title="测试话题")

        # 记录原始时间
        original_time = topic.updated_at

        # 等待一小段时间
        import time
        time.sleep(0.01)

        # 更新时间戳
        topic.update_timestamp()

        # 验证时间已更新
        assert topic.updated_at > original_time
