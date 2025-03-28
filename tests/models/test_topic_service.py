"""
测试TopicService模块

详细测试TopicService的核心功能和业务逻辑，
包括话题的获取、保存、选择和状态管理。
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import time

# 导入被测试模块
from core.models.service.topic_service import TopicService

class TestTopicServiceCore:
    """测试TopicService的核心功能"""

    @patch('core.models.topic_service.DBAdapter')
    def test_get_topic_found(self, mock_db_adapter):
        """测试获取存在的话题"""
        # 准备模拟数据
        mock_topic_dict = {
            "id": "test_id",
            "title": "测试话题",
            "platform": "weibo"
        }

        # 设置模拟行为
        mock_db_adapter.get_topic.return_value = mock_topic_dict

        # 模拟Topic.from_dict方法
        with patch('core.models.topic.Topic.from_dict', return_value=MagicMock()) as mock_from_dict:
            # 调用被测方法
            result = TopicService.get_topic("test_id")

            # 验证结果
            assert result is not None
            mock_db_adapter.get_topic.assert_called_once_with("test_id")
            mock_from_dict.assert_called_once_with(mock_topic_dict)

    @patch('core.models.topic_service.DBAdapter')
    def test_get_topic_not_found(self, mock_db_adapter):
        """测试获取不存在的话题"""
        # 设置模拟行为
        mock_db_adapter.get_topic.return_value = None

        # 调用被测方法
        result = TopicService.get_topic("nonexistent_id")

        # 验证结果
        assert result is None
        mock_db_adapter.get_topic.assert_called_once_with("nonexistent_id")

    @patch('core.models.topic_service.DBAdapter')
    def test_save_topic(self, mock_db_adapter):
        """测试保存话题"""
        # 准备模拟数据
        mock_topic = MagicMock()
        mock_topic.id = "test_id"
        mock_topic.title = "测试话题"

        # 设置模拟行为
        mock_db_adapter.save_topic.return_value = True

        # 调用被测方法
        result = TopicService.save_topic(mock_topic)

        # 验证结果
        assert result is True
        mock_db_adapter.save_topic.assert_called_once_with(mock_topic)

    @patch('core.models.topic_service.DBAdapter')
    def test_update_topic_status(self, mock_db_adapter):
        """测试更新话题状态"""
        # 设置模拟行为
        mock_db_adapter.update_topic_status.return_value = True

        # 调用被测方法
        result = TopicService.update_topic_status("test_id", "selected")

        # 验证结果
        assert result is True
        mock_db_adapter.update_topic_status.assert_called_once_with("test_id", "selected")

    @patch('core.models.topic_service.DBAdapter')
    def test_get_topics_by_platform(self, mock_db_adapter):
        """测试获取指定平台的话题列表"""
        # 准备模拟数据
        mock_topics = [
            {"id": "topic1", "title": "话题1", "platform": "weibo"},
            {"id": "topic2", "title": "话题2", "platform": "weibo"}
        ]

        # 设置模拟行为
        mock_db_adapter.get_topics_by_platform.return_value = mock_topics

        # 模拟Topic.from_dict方法
        with patch('core.models.topic.Topic.from_dict') as mock_from_dict:
            # 设置每次调用的返回值
            mock_from_dict.side_effect = [MagicMock(), MagicMock()]

            # 调用被测方法
            result = TopicService.get_topics_by_platform("weibo")

            # 验证结果
            assert len(result) == 2
            mock_db_adapter.get_topics_by_platform.assert_called_once_with("weibo")
            assert mock_from_dict.call_count == 2

    @patch('core.models.topic_service.DBAdapter')
    @patch('core.models.topic_service.time.time')
    def test_select_topic_with_content_type_filter(self, mock_time, mock_db_adapter):
        """测试按内容类型筛选话题"""
        # 准备模拟数据
        current_time = int(datetime.now().timestamp())
        mock_time.return_value = current_time

        mock_topics = [
            {"id": "topic1", "title": "通用话题", "platform": "weibo", "hot": 100, "trend_score": 0.5, "fetch_time": current_time},
            {"id": "topic2", "title": "文章话题", "platform": "weibo", "hot": 200, "trend_score": 0.8, "fetch_time": current_time, "content_type": "article"},
            {"id": "topic3", "title": "视频话题", "platform": "weibo", "hot": 300, "trend_score": 0.9, "fetch_time": current_time, "content_type": "video"}
        ]

        # 设置模拟行为
        mock_db_adapter.get_topics_by_status.return_value = mock_topics
        mock_db_adapter.update_topic_status.return_value = True

        # 模拟Topic.from_dict方法
        with patch('core.models.topic.Topic.from_dict') as mock_from_dict:
            # 设置返回值
            mock_topic = MagicMock()
            mock_topic.id = "topic2"
            mock_from_dict.return_value = mock_topic

            # 应该选择内容类型匹配的话题
            assert mock_from_dict.call_args[0][0]["content_type"] == "article"
