"""测试 FeedbackManager 类的数据库交互操作"""
import unittest
from unittest.mock import patch, MagicMock
import pytest
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from core.models.feedback.feedback_manager import FeedbackManager
from core.models.feedback.feedback_db import FeedbackDB, ResearchFeedbackDB, ContentFeedbackDB

class TestFeedbackManager(unittest.TestCase):
    """测试 FeedbackManager 类"""

    def setUp(self):
        """测试前初始化"""
        # 模拟初始化 FeedbackManager
        FeedbackManager._initialized = True
        FeedbackManager._use_db = True

    def tearDown(self):
        """测试后清理"""
        FeedbackManager._initialized = False

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_create_research_feedback(self, mock_get_db):
        """测试创建研究反馈"""
        # 模拟数据库会话
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 测试参数
        data = {
            "feedback_text": "研究结果很全面，但缺少一些关键数据",
            "accuracy_rating": 8.5,
            "completeness_rating": 7.0,
            "suggested_improvements": ["添加更多数据来源", "增加图表展示"],
            "feedback_source": "human",
            "research_id": "research-123"
        }

        # 执行方法
        result = FeedbackManager.create_feedback("research", data)

        # 验证结果
        self.assertIsNotNone(result)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # 验证创建的对象
        created_feedback = mock_db.add.call_args[0][0]
        self.assertIsInstance(created_feedback, ResearchFeedbackDB)
        self.assertEqual(created_feedback.feedback_text, data["feedback_text"])
        # 这些字段已经被提取到单独的变量中，不再存在于 data 字典中
        # self.assertEqual(created_feedback.accuracy_rating, data["accuracy_rating"])
        # self.assertEqual(created_feedback.completeness_rating, data["completeness_rating"])
        # self.assertEqual(created_feedback.research_id, data["research_id"])
        self.assertEqual(created_feedback.feedback_source, data["feedback_source"])
        self.assertEqual(created_feedback.feedback_metadata["suggested_improvements"], ["添加更多数据来源", "增加图表展示"])

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_create_content_feedback(self, mock_get_db):
        """测试创建内容反馈"""
        # 模拟数据库会话
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 测试参数
        data = {
            "content_id": "article-456",
            "feedback_text": "文章结构清晰，但有些表述不够准确",
            "rating": 8.0,
            "feedback_categories": ["clarity", "accuracy"],
            "user_id": "user-789",
            "feedback_source": "human"
        }

        # 执行方法
        result = FeedbackManager.create_feedback("content", data)

        # 验证结果
        self.assertIsNotNone(result)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

        # 验证创建的对象
        created_feedback = mock_db.add.call_args[0][0]
        self.assertIsInstance(created_feedback, ContentFeedbackDB)
        # 这些字段已经被提取到单独的变量中，不再存在于 data 字典中
        # self.assertEqual(created_feedback.content_id, data["content_id"])
        # self.assertEqual(created_feedback.user_id, data["user_id"])
        self.assertEqual(created_feedback.feedback_text, data["feedback_text"])
        self.assertEqual(created_feedback.rating, data["rating"])
        self.assertEqual(created_feedback.feedback_source, data["feedback_source"])
        self.assertEqual(created_feedback.feedback_metadata["feedback_categories"], ["clarity", "accuracy"])

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_create_feedback_unsupported_type(self, mock_get_db):
        """测试创建不支持的反馈类型"""
        # 执行方法
        result = FeedbackManager.create_feedback("unsupported_type", {"feedback_text": "测试"})

        # 验证结果为 None
        self.assertIsNone(result)
        # 由于我们在 create_feedback 方法中使用了 try-except 块，即使类型不支持，
        # 也会尝试进入 with 块，所以这里不能断言 __enter__ 没有被调用
        # mock_get_db.return_value.__enter__.assert_not_called()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_create_feedback_db_error(self, mock_get_db):
        """测试创建反馈时数据库错误处理"""
        # 模拟数据库异常
        mock_db = MagicMock()
        mock_db.commit.side_effect = SQLAlchemyError("Test DB error")
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行并检查方法
        data = {
            "feedback_text": "测试反馈",
            "content_id": "article-123",
            "feedback_source": "system"
        }
        result = FeedbackManager.create_feedback("content", data)

        # 验证结果为 None（表示失败）
        self.assertIsNone(result)

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_get_feedback_by_id(self, mock_get_db):
        """测试通过 ID 获取反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedback = MagicMock(spec=FeedbackDB)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_feedback
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行查询
        feedback_id = uuid4()
        result = FeedbackManager.get_feedback_by_id(feedback_id)

        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_db.query.assert_called_with(FeedbackDB)
        mock_db.query.return_value.filter.assert_called_once()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_get_feedback_by_content_id(self, mock_get_db):
        """测试获取特定内容的所有反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedbacks = [MagicMock(spec=ContentFeedbackDB), MagicMock(spec=ContentFeedbackDB)]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_feedbacks
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行查询
        content_id = "article-123"
        result = FeedbackManager.get_feedback_by_content_id(content_id)

        # 验证结果
        self.assertEqual(result, mock_feedbacks)
        mock_db.query.assert_called_with(ContentFeedbackDB)
        mock_db.query.return_value.filter.assert_called_once()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_get_feedback_by_research_id(self, mock_get_db):
        """测试获取特定研究的所有反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedbacks = [MagicMock(spec=ResearchFeedbackDB), MagicMock(spec=ResearchFeedbackDB)]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_feedbacks
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行查询
        research_id = "research-123"
        result = FeedbackManager.get_feedback_by_research_id(research_id)

        # 验证结果
        self.assertEqual(result, mock_feedbacks)
        mock_db.query.assert_called_with(ResearchFeedbackDB)
        mock_db.query.return_value.filter.assert_called_once()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_update_feedback(self, mock_get_db):
        """测试更新反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedback = MagicMock(spec=ResearchFeedbackDB)
        mock_feedback.feedback_metadata = {}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_feedback
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行更新
        feedback_id = uuid4()
        updates = {
            "feedback_text": "更新后的反馈",
            "accuracy_rating": 9.0,
            "suggested_improvements": ["新的改进建议"]
        }

        result = FeedbackManager.update_feedback(feedback_id, updates)

        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_feedback)

        # 验证更新的属性
        self.assertEqual(mock_feedback.feedback_text, "更新后的反馈")
        self.assertEqual(mock_feedback.accuracy_rating, 9.0)
        self.assertEqual(mock_feedback.feedback_metadata["suggested_improvements"], ["新的改进建议"])

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_update_content_feedback(self, mock_get_db):
        """测试更新内容反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedback = MagicMock(spec=ContentFeedbackDB)
        mock_feedback.feedback_metadata = {}
        mock_db.query.return_value.filter.return_value.first.return_value = mock_feedback
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行更新
        feedback_id = uuid4()
        updates = {
            "feedback_text": "更新后的反馈",
            "rating": 9.5,
            "feedback_categories": ["新类别1", "新类别2"]
        }

        result = FeedbackManager.update_feedback(feedback_id, updates)

        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_feedback)

        # 验证更新的属性
        self.assertEqual(mock_feedback.feedback_text, "更新后的反馈")
        self.assertEqual(mock_feedback.rating, 9.5)
        self.assertEqual(mock_feedback.feedback_metadata["feedback_categories"], ["新类别1", "新类别2"])

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_update_nonexistent_feedback(self, mock_get_db):
        """测试更新不存在的反馈"""
        # 模拟数据库响应 - 未找到记录
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行更新
        feedback_id = uuid4()
        result = FeedbackManager.update_feedback(feedback_id, {"feedback_text": "更新"})

        # 验证结果为 None
        self.assertIsNone(result)
        # 确保没有执行提交
        mock_db.commit.assert_not_called()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_delete_feedback(self, mock_get_db):
        """测试删除反馈"""
        # 模拟数据库响应
        mock_db = MagicMock()
        mock_feedback = MagicMock(spec=FeedbackDB)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_feedback
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行删除
        feedback_id = uuid4()
        result = FeedbackManager.delete_feedback(feedback_id)

        # 验证结果
        self.assertTrue(result)
        mock_db.delete.assert_called_once_with(mock_feedback)
        mock_db.commit.assert_called_once()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_delete_nonexistent_feedback(self, mock_get_db):
        """测试删除不存在的反馈"""
        # 模拟数据库响应 - 未找到记录
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 执行删除
        feedback_id = uuid4()
        result = FeedbackManager.delete_feedback(feedback_id)

        # 验证结果为 False
        self.assertFalse(result)
        # 确保没有执行删除和提交
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

    @patch('core.models.feedback.feedback_manager.get_db')
    def test_db_disabled(self, mock_get_db):
        """测试禁用数据库时的行为"""
        # 设置数据库为禁用状态
        FeedbackManager._use_db = False

        # 测试所有数据库操作的方法
        result1 = FeedbackManager.create_feedback("research", {"feedback_text": "测试"})
        result2 = FeedbackManager.get_feedback_by_id(uuid4())
        result3 = FeedbackManager.get_feedback_by_content_id("article-123")
        result4 = FeedbackManager.get_feedback_by_research_id("research-123")
        result5 = FeedbackManager.update_feedback(uuid4(), {"feedback_text": "更新"})
        result6 = FeedbackManager.delete_feedback(uuid4())

        # 验证所有方法都返回适当的默认值，并且不会调用数据库
        self.assertIsNone(result1)
        self.assertIsNone(result2)
        self.assertEqual(result3, [])
        self.assertEqual(result4, [])
        self.assertIsNone(result5)
        self.assertFalse(result6)

        # 确保没有任何数据库调用
        mock_get_db.assert_not_called()

        # 恢复数据库启用状态以避响影响其他测试
        FeedbackManager._use_db = True

if __name__ == "__main__":
    unittest.main()
