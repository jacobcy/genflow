"""
测试Topic模型

专注测试Topic模型的创建、属性、序列化和验证功能，
确保模型的基本功能正确无误。
"""

import pytest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

# 导入被测试模块
from core.models.topic import Topic

class TestTopicCreation:
    """测试Topic创建功能"""

    def test_create_topic_with_all_fields(self):
        """测试创建包含所有字段的话题"""
        # 创建话题实例
        topic = Topic(
            id="test_id",
            title="测试话题",
            platform="weibo",
            url="http://example.com/topic",
            hot=1000,
            trend_score=0.8,
            categories=["科技", "AI"],
            tags=["人工智能", "机器学习"],
            fetch_time=int(datetime.now().timestamp()),
            status="pending"
        )

        # 验证属性
        assert topic.id == "test_id"
        assert topic.title == "测试话题"
        assert topic.platform == "weibo"
        assert topic.url == "http://example.com/topic"
        assert topic.hot == 1000
        assert topic.trend_score == 0.8
        assert "科技" in topic.categories
        assert "AI" in topic.categories
        assert "人工智能" in topic.tags
        assert "机器学习" in topic.tags
        assert topic.status == "pending"

    def test_create_topic_with_minimal_fields(self):
        """测试创建只包含必要字段的话题"""
        # 创建话题实例
        topic = Topic(
            title="测试话题",
            platform="weibo"
        )

        # 验证属性
        assert topic.title == "测试话题"
        assert topic.platform == "weibo"
        assert topic.id is not None  # 应自动生成ID
        assert isinstance(topic.id, str)
        assert topic.hot == 0  # 默认值
        assert topic.trend_score == 0.0  # 默认值
        assert topic.categories == []  # 默认值
        assert topic.tags == []  # 默认值
        assert topic.status == "pending"  # 默认值

    @patch('uuid.uuid4')
    def test_auto_generate_id(self, mock_uuid):
        """测试自动生成ID功能"""
        # 设置模拟行为
        mock_uuid_str = "generated-uuid"
        mock_uuid_obj = MagicMock()
        mock_uuid_obj.hex = mock_uuid_str
        mock_uuid.return_value = mock_uuid_obj

        # 创建话题实例，不指定ID
        topic = Topic(
            title="测试话题",
            platform="weibo"
        )

        # 由于ID格式为 platform_timestamp_uuid[:8]，验证ID的结构
        id_parts = topic.id.split('_')
        assert len(id_parts) == 3
        assert id_parts[0] == "weibo"  # 平台
        assert id_parts[2] == mock_uuid_str[:8]  # UUID的前8个字符

        # 验证mock被调用
        mock_uuid.assert_called_once()

class TestTopicSerialization:
    """测试Topic序列化功能"""

    def test_to_dict(self):
        """测试话题转换为字典"""
        # 创建当前时间戳
        current_time = int(datetime.now().timestamp())

        # 创建话题实例
        topic = Topic(
            id="test_id",
            title="测试话题",
            platform="weibo",
            url="http://example.com/topic",
            hot=1000,
            trend_score=0.8,
            categories=["科技", "AI"],
            tags=["人工智能", "机器学习"],
            fetch_time=current_time,
            status="pending"
        )

        # 调用to_dict方法
        result = topic.to_dict()

        # 验证结果
        assert result["id"] == "test_id"
        assert result["title"] == "测试话题"
        assert result["platform"] == "weibo"
        assert result["url"] == "http://example.com/topic"
        assert result["hot"] == 1000
        assert result["trend_score"] == 0.8
        assert result["categories"] == ["科技", "AI"]
        assert result["tags"] == ["人工智能", "机器学习"]
        assert result["fetch_time"] == current_time
        assert result["status"] == "pending"

    def test_from_dict(self):
        """测试从字典创建话题"""
        # 准备话题字典
        current_time = int(datetime.now().timestamp())
        topic_dict = {
            "id": "test_id",
            "title": "测试话题",
            "platform": "weibo",
            "url": "http://example.com/topic",
            "hot": 1000,
            "trend_score": 0.8,
            "categories": ["科技", "AI"],
            "tags": ["人工智能", "机器学习"],
            "fetch_time": current_time,
            "status": "pending"
        }

        # 调用from_dict方法
        topic = Topic.from_dict(topic_dict)

        # 验证结果
        assert topic.id == "test_id"
        assert topic.title == "测试话题"
        assert topic.platform == "weibo"
        assert topic.url == "http://example.com/topic"
        assert topic.hot == 1000
        assert topic.trend_score == 0.8
        assert topic.categories == ["科技", "AI"]
        assert topic.tags == ["人工智能", "机器学习"]
        assert topic.fetch_time == current_time
        assert topic.status == "pending"

    def test_from_dict_minimal(self):
        """测试从最小字典创建话题"""
        # 准备最小话题字典
        topic_dict = {
            "title": "测试话题",
            "platform": "weibo"
        }

        # 调用from_dict方法
        topic = Topic.from_dict(topic_dict)

        # 打印用于诊断
        print(f"Categories: {topic.categories}")
        print(f"Platform: {topic.platform}")

        # 验证结果
        assert topic.title == "测试话题"
        assert topic.platform == "weibo"
        assert topic.id is not None  # 应自动生成ID
        assert topic.hot == 0  # 默认值

        # 测试平台默认分类
        # weibo平台的默认分类是"社交"
        assert topic.categories == ['社交']

class TestTopicValidation:
    """测试Topic数据验证功能"""

    def test_validate_required_fields(self):
        """测试必填字段验证"""
        # 缺少title字段
        with pytest.raises(ValueError):
            Topic(platform="weibo")

        # 缺少platform字段
        with pytest.raises(ValueError):
            Topic(title="测试话题")

    def test_validate_hot_value(self):
        """测试热度值验证"""
        # 负热度值
        with pytest.raises(ValueError):
            Topic(title="测试话题", platform="weibo", hot=-10)

        # 热度值过大
        with pytest.raises(ValueError):
            Topic(title="测试话题", platform="weibo", hot=1000000000)

    def test_validate_trend_score(self):
        """测试趋势得分验证"""
        # 负趋势得分
        with pytest.raises(ValueError):
            Topic(title="测试话题", platform="weibo", trend_score=-0.1)

        # 趋势得分超过1
        with pytest.raises(ValueError):
            Topic(title="测试话题", platform="weibo", trend_score=1.1)
