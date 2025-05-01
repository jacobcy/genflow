"""
测试TopicManager

测试TopicManager的数据持久化功能，包括获取、保存和删除话题。
"""

from unittest.mock import patch, MagicMock

from core.models.topic.topic import Topic
from core.models.topic.topic_manager import TopicManager


class TestTopicManager:
    """测试TopicManager功能"""

    def setup_method(self):
        """测试前设置"""
        # 确保每个测试前重置初始化状态
        TopicManager._initialized = False

    @patch('core.models.topic.topic_manager.get_db')
    def test_initialize(self, mock_get_db):
        """测试初始化"""
        # 调用被测试方法
        TopicManager.initialize()

        # 验证结果
        assert TopicManager._initialized is True
        assert TopicManager._use_db is True

    @patch('core.models.topic.topic_manager.get_db')
    def test_ensure_initialized(self, mock_get_db):
        """测试确保初始化"""
        # 设置未初始化状态
        TopicManager._initialized = False

        # 调用被测试方法
        TopicManager.ensure_initialized()

        # 验证结果
        assert TopicManager._initialized is True

    @patch('core.models.topic.topic_manager.get_db')
    def test_get_topic(self, mock_get_db):
        """测试获取话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果
        mock_topic_db = MagicMock()
        mock_topic_db.id = "test_id"
        mock_topic_db.title = "测试话题"
        mock_topic_db.description = "这是一个测试话题"
        mock_topic_db.platform = "medium"
        mock_topic_db.url = "https://example.com"
        mock_topic_db.mobile_url = "https://m.example.com"
        mock_topic_db.hot = 100
        mock_topic_db.cover = "https://example.com/image.jpg"
        mock_topic_db.created_at = 1650000000
        mock_topic_db.updated_at = 1650000000
        mock_topic_db.source_time = 1650000000
        mock_topic_db.expire_time = 1650000000
        mock_session.query.return_value.filter.return_value.first.return_value = mock_topic_db

        # 初始化管理器
        TopicManager.initialize()

        # 调用被测试方法
        result = TopicManager.get_topic("test_id")

        # 验证结果
        assert result is not None
        assert result.id == "test_id"
        assert result.title == "测试话题"
        mock_session.query.assert_called_once()

    @patch('core.models.topic.topic_manager.get_db')
    def test_get_topic_not_found(self, mock_get_db):
        """测试获取不存在的话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果为None
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # 初始化管理器
        TopicManager.initialize()

        # 调用被测试方法
        result = TopicManager.get_topic("nonexistent_id")

        # 验证结果
        assert result is None
        mock_session.query.assert_called_once()

    @patch('core.models.topic.topic_manager.get_db')
    def test_save_topic_new(self, mock_get_db):
        """测试保存新话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果为None（话题不存在）
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # 初始化管理器
        TopicManager.initialize()

        # 创建测试话题
        topic = Topic(
            id="test_id",
            title="测试话题",
            description="这是一个测试话题",
            platform="medium"
        )

        # 调用被测试方法
        result = TopicManager.save_topic(topic)

        # 验证结果
        assert result is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('core.models.topic.topic_manager.get_db')
    def test_save_topic_existing(self, mock_get_db):
        """测试更新现有话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果（话题存在）
        mock_topic_db = MagicMock()
        mock_topic_db.id = "test_id"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_topic_db

        # 初始化管理器
        TopicManager.initialize()

        # 创建测试话题
        topic = Topic(
            id="test_id",
            title="更新的测试话题",
            description="这是一个更新的测试话题",
            platform="medium"
        )

        # 调用被测试方法
        result = TopicManager.save_topic(topic)

        # 验证结果
        assert result is True
        mock_session.add.assert_not_called()  # 不应调用add
        mock_session.commit.assert_called_once()

    @patch('core.models.topic.topic_manager.get_db')
    def test_delete_topic(self, mock_get_db):
        """测试删除话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果
        mock_topic_db = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_topic_db

        # 初始化管理器
        TopicManager.initialize()

        # 调用被测试方法
        result = TopicManager.delete_topic("test_id")

        # 验证结果
        assert result is True
        mock_session.delete.assert_called_once_with(mock_topic_db)
        mock_session.commit.assert_called_once()

    @patch('core.models.topic.topic_manager.get_db')
    def test_delete_topic_not_found(self, mock_get_db):
        """测试删除不存在的话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果为None
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # 初始化管理器
        TopicManager.initialize()

        # 调用被测试方法
        result = TopicManager.delete_topic("nonexistent_id")

        # 验证结果
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('core.models.topic.topic_manager.get_db')
    def test_get_topics_by_platform(self, mock_get_db):
        """测试按平台获取话题"""
        # 设置模拟数据库会话
        mock_session = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_session

        # 设置模拟查询结果
        mock_topic_db1 = MagicMock()
        mock_topic_db1.id = "test1"
        mock_topic_db1.title = "测试话题1"
        mock_topic_db1.description = "这是测试话题1"
        mock_topic_db1.platform = "medium"
        mock_topic_db1.url = "https://example.com/1"
        mock_topic_db1.mobile_url = "https://m.example.com/1"
        mock_topic_db1.hot = 100
        mock_topic_db1.cover = "https://example.com/image1.jpg"
        mock_topic_db1.created_at = 1650000000
        mock_topic_db1.updated_at = 1650000000
        mock_topic_db1.source_time = 1650000000
        mock_topic_db1.expire_time = 1650000000

        mock_topic_db2 = MagicMock()
        mock_topic_db2.id = "test2"
        mock_topic_db2.title = "测试话题2"
        mock_topic_db2.description = "这是测试话题2"
        mock_topic_db2.platform = "medium"
        mock_topic_db2.url = "https://example.com/2"
        mock_topic_db2.mobile_url = "https://m.example.com/2"
        mock_topic_db2.hot = 200
        mock_topic_db2.cover = "https://example.com/image2.jpg"
        mock_topic_db2.created_at = 1650000000
        mock_topic_db2.updated_at = 1650000000
        mock_topic_db2.source_time = 1650000000
        mock_topic_db2.expire_time = 1650000000

        mock_session.query.return_value.filter.return_value.all.return_value = [
            mock_topic_db1, mock_topic_db2
        ]

        # 初始化管理器
        TopicManager.initialize()

        # 调用被测试方法
        result = TopicManager.get_topics_by_platform("medium")

        # 验证结果
        assert len(result) == 2
        assert result[0].id == "test1"
        assert result[1].id == "test2"
        mock_session.query.assert_called_once()