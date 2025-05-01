"""
测试TopicFactory

测试TopicFactory的业务逻辑功能，包括获取、保存和删除话题。
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from core.models.topic.topic import Topic
from core.models.topic.topic_factory import TopicFactory


class TestTopicFactory:
    """测试TopicFactory功能"""

    @patch('core.models.topic.topic_factory.TopicManager')
    def test_get_topic(self, mock_manager):
        """测试获取话题"""
        # 设置模拟返回值
        mock_topic = Topic(
            id="test_id",
            title="测试话题",
            description="这是一个测试话题",
            platform="medium"
        )
        mock_manager.get_topic.return_value = mock_topic

        # 调用被测试方法
        result = TopicFactory.get_topic("test_id")

        # 验证结果
        assert result is not None
        assert result.id == "test_id"
        assert result.title == "测试话题"
        mock_manager.get_topic.assert_called_once_with("test_id")

    @patch('core.models.topic.topic_factory.TopicManager')
    def test_save_topic(self, mock_manager):
        """测试保存话题"""
        # 设置模拟返回值
        mock_manager.save_topic.return_value = True

        # 创建测试话题
        topic = Topic(
            id="test_id",
            title="测试话题",
            description="这是一个测试话题",
            platform="medium"
        )

        # 记录原始更新时间
        original_time = topic.updated_at

        # 调用被测试方法
        result = TopicFactory.save_topic(topic)

        # 验证结果
        assert result is True
        assert topic.updated_at > original_time  # 验证时间戳已更新
        mock_manager.save_topic.assert_called_once()

    @patch('core.models.topic.topic_factory.TopicManager')
    def test_save_topic_invalid_type(self, mock_manager):
        """测试保存无效类型的话题"""
        # 调用被测试方法，传入非Topic对象
        result = TopicFactory.save_topic("not a topic")

        # 验证结果
        assert result is False
        mock_manager.save_topic.assert_not_called()

    @patch('core.models.topic.topic_factory.TopicManager')
    def test_delete_topic(self, mock_manager):
        """测试删除话题"""
        # 设置模拟返回值
        mock_manager.delete_topic.return_value = True

        # 调用被测试方法
        result = TopicFactory.delete_topic("test_id")

        # 验证结果
        assert result is True
        mock_manager.delete_topic.assert_called_once_with("test_id")

    @patch('core.models.topic.topic_factory.TopicManager')
    def test_get_topics_by_platform(self, mock_manager):
        """测试按平台获取话题"""
        # 设置模拟返回值
        mock_topics = [
            Topic(id="test1", title="测试话题1", platform="medium"),
            Topic(id="test2", title="测试话题2", platform="medium")
        ]
        mock_manager.get_topics_by_platform.return_value = mock_topics

        # 调用被测试方法
        result = TopicFactory.get_topics_by_platform("medium")

        # 验证结果
        assert len(result) == 2
        assert result[0].id == "test1"
        assert result[1].id == "test2"
        mock_manager.get_topics_by_platform.assert_called_once_with("medium")