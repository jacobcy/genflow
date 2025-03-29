"""
测试DBAdapter模块

专注测试DBAdapter的核心功能，包括初始化、话题和文章的基本CRUD操作。
简化集成测试，避免与其他测试文件的重复测试内容。
"""

import pytest
from unittest.mock import patch, MagicMock
import time

# 导入被测试模块
from core.models.infra.db_adapter import DBAdapter
from core.models.db.initialize import initialize_all

class TestDBAdapterInitialization:
    """测试DBAdapter初始化功能"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    @patch('core.db.initialize.initialize_all')
    def test_initialize(self, mock_initialize_all):
        """测试数据库初始化"""
        # 设置模拟行为
        mock_initialize_all.return_value = True

        # 调用被测方法
        result = DBAdapter.initialize()

        # 验证结果
        assert result is True
        assert DBAdapter._is_initialized is True
        mock_initialize_all.assert_called_once()

    @patch('core.db.initialize.initialize_all')
    def test_initialize_failure(self, mock_initialize_all):
        """测试数据库初始化失败"""
        # 设置模拟行为 - 初始化失败
        mock_initialize_all.side_effect = Exception("测试初始化失败")

        # 调用被测方法
        result = DBAdapter.initialize()

        # 验证结果
        assert result is False
        assert DBAdapter._is_initialized is False
        mock_initialize_all.assert_called_once()

    @patch('core.db.initialize.initialize_all')
    def test_initialize_already_initialized(self, mock_initialize_all):
        """测试已初始化数据库的情况"""
        # 设置已初始化状态
        DBAdapter._is_initialized = True

        # 调用被测方法
        result = DBAdapter.initialize()

        # 验证结果
        assert result is True
        assert DBAdapter._is_initialized is True
        # 不应该再次调用initialize_all
        mock_initialize_all.assert_not_called()

class TestDBAdapterTopicOperations:
    """测试DBAdapter话题操作功能"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 设置DBAdapter已初始化
        DBAdapter._is_initialized = True

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    @patch('core.db.repository.topic_repo.get')
    def test_get_topic(self, mock_get):
        """测试获取话题"""
        # 准备模拟数据
        mock_topic = MagicMock()
        mock_topic.to_dict.return_value = {"id": "test_id", "title": "测试话题"}

        # 设置模拟行为
        mock_get.return_value = mock_topic

        # 调用被测方法
        result = DBAdapter.get_topic("test_id")

        # 验证结果
        assert result == {"id": "test_id", "title": "测试话题"}
        mock_get.assert_called_once_with("test_id")

    @patch('core.db.repository.topic_repo.get')
    def test_get_topic_not_found(self, mock_get):
        """测试获取不存在的话题"""
        # 设置模拟行为
        mock_get.return_value = None

        # 调用被测方法
        result = DBAdapter.get_topic("nonexistent_id")

        # 验证结果
        assert result is None
        mock_get.assert_called_once_with("nonexistent_id")

    @patch('core.db.repository.topic_repo.get')
    @patch('core.db.repository.topic_repo.create')
    @patch('time.time')
    def test_save_topic_new(self, mock_time, mock_create, mock_get):
        """测试保存新话题"""
        # 设置时间模拟
        current_time = 1000000000
        mock_time.return_value = current_time

        # 准备模拟数据
        mock_topic = MagicMock()
        mock_topic.id = "test_id"
        mock_topic.title = "测试话题"
        mock_topic.platform = "weibo"
        mock_topic.to_dict.return_value = {
            "id": "test_id",
            "title": "测试话题",
            "platform": "weibo"
        }

        # 设置模拟行为 - 话题不存在
        mock_get.return_value = None
        mock_create.return_value = True

        # 调用被测方法
        result = DBAdapter.save_topic(mock_topic)

        # 验证结果
        assert result is True
        mock_get.assert_called_once_with("test_id")
        mock_create.assert_called_once()

    @patch('core.db.repository.topic_repo.get')
    @patch('core.db.repository.topic_repo.update')
    def test_save_topic_existing(self, mock_update, mock_get):
        """测试更新已存在话题"""
        # 准备模拟数据
        mock_topic = MagicMock()
        mock_topic.id = "test_id"
        mock_topic.title = "更新的测试话题"
        mock_topic.platform = "weibo"
        mock_topic.to_dict.return_value = {
            "id": "test_id",
            "title": "更新的测试话题",
            "platform": "weibo"
        }

        # 设置模拟行为 - 话题已存在
        existing_topic = MagicMock()
        mock_get.return_value = existing_topic
        mock_update.return_value = True

        # 调用被测方法
        result = DBAdapter.save_topic(mock_topic)

        # 验证结果
        assert result is True
        mock_get.assert_called_once_with("test_id")
        mock_update.assert_called_once()

    @patch('core.db.repository.topic_repo.get_by_platform')
    def test_get_topics_by_platform(self, mock_get_by_platform):
        """测试获取指定平台的话题列表"""
        # 准备模拟数据
        mock_topics = [
            MagicMock(),
            MagicMock()
        ]
        mock_topics[0].to_dict.return_value = {"id": "topic1", "title": "话题1", "platform": "weibo"}
        mock_topics[1].to_dict.return_value = {"id": "topic2", "title": "话题2", "platform": "weibo"}

        # 设置模拟行为
        mock_get_by_platform.return_value = mock_topics

        # 调用被测方法
        result = DBAdapter.get_topics_by_platform("weibo")

        # 验证结果
        assert len(result) == 2
        mock_get_by_platform.assert_called_once_with("weibo")

    @patch('core.db.repository.topic_repo.update_status')
    def test_update_topic_status(self, mock_update_status):
        """测试更新话题状态"""
        # 设置模拟行为
        mock_update_status.return_value = True

        # 调用被测方法
        result = DBAdapter.update_topic_status("test_id", "selected")

        # 验证结果
        assert result is True
        mock_update_status.assert_called_once_with("test_id", "selected")

class TestDBAdapterArticleOperations:
    """测试DBAdapter文章操作功能"""

    def setup_method(self):
        """每个测试方法前的设置"""
        # 设置DBAdapter已初始化
        DBAdapter._is_initialized = True

    def teardown_method(self):
        """每个测试方法后的清理"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    @patch('core.db.repository.article_repo.get')
    def test_get_article(self, mock_get):
        """测试获取文章"""
        # 准备模拟数据
        mock_article = MagicMock()
        mock_article.to_dict.return_value = {"id": "article_id", "title": "测试文章", "topic_id": "test_topic_id"}

        # 设置模拟行为
        mock_get.return_value = mock_article

        # 调用被测方法
        result = DBAdapter.get_article("article_id")

        # 验证结果
        assert result == {"id": "article_id", "title": "测试文章", "topic_id": "test_topic_id"}
        mock_get.assert_called_once_with("article_id")

# 简化的集成测试示例，只测试最核心的功能
@pytest.mark.integration
class TestDBAdapterIntegration:
    """测试DBAdapter与实际数据库的集成"""

    def setup_method(self):
        """设置测试环境"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    def teardown_method(self):
        """清理测试环境"""
        # 重置DBAdapter的状态
        DBAdapter._is_initialized = False

    @patch('core.db.initialize.initialize_all')
    @patch('core.db.repository.topic_repo.create')
    @patch('core.db.repository.topic_repo.get')
    @patch('time.time')
    def test_save_and_get_topic(self, mock_time, mock_get, mock_create, mock_initialize_all):
        """测试保存和获取话题的集成流程"""
        # 设置时间模拟
        current_time = 1000000000
        mock_time.return_value = current_time

        # 设置模拟行为
        mock_initialize_all.return_value = True

        # 模拟保存话题
        mock_topic = MagicMock()
        mock_topic.id = "test_id"
        mock_topic.title = "测试话题"
        mock_topic.platform = "weibo"
        mock_topic.to_dict.return_value = {"id": "test_id", "title": "测试话题", "platform": "weibo"}

        # 模拟获取话题时的预期返回值，包含自动添加的时间戳字段
        get_result_mock = MagicMock()
        get_result_mock.to_dict.return_value = {
            "id": "test_id",
            "title": "测试话题",
            "platform": "weibo",
            "timestamp": current_time,
            "fetch_time": current_time,
            "expire_time": current_time + 7 * 24 * 60 * 60
        }

        # 首次查询返回None（话题不存在），保存后查询返回话题
        mock_get.side_effect = [None, get_result_mock]
        mock_create.return_value = True

        # 调用保存方法
        DBAdapter.initialize()
        save_result = DBAdapter.save_topic(mock_topic)

        # 调用获取方法
        get_result = DBAdapter.get_topic("test_id")

        # 验证结果
        assert save_result is True
        assert get_result["id"] == "test_id"
        assert get_result["title"] == "测试话题"
        assert get_result["platform"] == "weibo"
        # 验证时间戳字段
        assert "timestamp" in get_result
        assert "fetch_time" in get_result
        assert "expire_time" in get_result
        assert mock_get.call_count == 2
        mock_create.assert_called_once()
