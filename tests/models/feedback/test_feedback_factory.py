"""测试 FeedbackFactory 类的协调功能"""
import unittest
from unittest.mock import patch, MagicMock
import pytest
from uuid import uuid4, UUID
from datetime import datetime, UTC

from core.models.feedback.feedback_factory import FeedbackFactory
from core.models.feedback.feedback_manager import FeedbackManager
from core.models.feedback.feedback import ResearchFeedback, ContentFeedback
from core.models.feedback.feedback_db import FeedbackDB, ResearchFeedbackDB, ContentFeedbackDB

class TestFeedbackFactory(unittest.TestCase):
    """测试 FeedbackFactory 类"""

    def setUp(self):
        """测试前初始化"""
        pass

    def tearDown(self):
        """测试后清理"""
        pass

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_create_research_feedback(self, mock_feedback_manager):
        """测试创建研究反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock(spec=ResearchFeedbackDB)
        mock_db_object.id = uuid4()
        mock_feedback_manager.create_feedback.return_value = mock_db_object

        # 测试参数
        feedback_text = "研究结果很全面，但缺少一些关键数据"
        accuracy_rating = 8.5
        completeness_rating = 7.0
        suggested_improvements = ["添加更多数据来源", "增加图表展示"]
        feedback_source = "human"
        research_id = "research-123"

        # 执行方法
        result = FeedbackFactory.create_research_feedback(
            feedback_text=feedback_text,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            suggested_improvements=suggested_improvements,
            feedback_source=feedback_source,
            research_id=research_id
        )

        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ResearchFeedback)
        self.assertEqual(result.feedback_text, feedback_text)
        self.assertEqual(result.accuracy_rating, accuracy_rating)
        self.assertEqual(result.completeness_rating, completeness_rating)
        self.assertEqual(result.suggested_improvements, suggested_improvements)
        self.assertEqual(result.feedback_source, feedback_source)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.create_feedback.assert_called_once()
        call_args = mock_feedback_manager.create_feedback.call_args
        self.assertEqual(call_args[0][0], "research")  # 检查反馈类型
        data = call_args[0][1]  # 获取数据字典
        self.assertEqual(data["feedback_text"], feedback_text)
        self.assertEqual(data["accuracy_rating"], accuracy_rating)
        self.assertEqual(data["completeness_rating"], completeness_rating)
        self.assertEqual(data["suggested_improvements"], suggested_improvements)
        self.assertEqual(data["feedback_source"], feedback_source)
        self.assertEqual(data["research_id"], research_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_create_content_feedback(self, mock_feedback_manager):
        """测试创建内容反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock(spec=ContentFeedbackDB)
        mock_db_object.id = uuid4()
        mock_feedback_manager.create_feedback.return_value = mock_db_object

        # 测试参数
        content_id = "article-456"
        feedback_text = "文章结构清晰，但有些表述不够准确"
        rating = 8.0
        feedback_categories = ["clarity", "accuracy"]
        user_id = "user-789"

        # 执行方法
        result = FeedbackFactory.create_content_feedback(
            content_id=content_id,
            feedback_text=feedback_text,
            rating=rating,
            feedback_categories=feedback_categories,
            user_id=user_id
        )

        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ContentFeedback)
        self.assertEqual(result.content_id, content_id)
        self.assertEqual(result.feedback_text, feedback_text)
        self.assertEqual(result.rating, rating)
        self.assertEqual(result.feedback_categories, feedback_categories)
        self.assertEqual(result.user_id, user_id)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.create_feedback.assert_called_once()
        call_args = mock_feedback_manager.create_feedback.call_args
        self.assertEqual(call_args[0][0], "content")  # 检查反馈类型
        data = call_args[0][1]  # 获取数据字典
        self.assertEqual(data["content_id"], content_id)
        self.assertEqual(data["feedback_text"], feedback_text)
        self.assertEqual(data["rating"], rating)
        self.assertEqual(data["feedback_categories"], feedback_categories)
        self.assertEqual(data["user_id"], user_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_create_feedback_db_failure(self, mock_feedback_manager):
        """测试创建反馈时数据库失败的情况"""
        # 模拟 FeedbackManager 返回 None 表示数据库操作失败
        mock_feedback_manager.create_feedback.return_value = None

        # 执行方法
        result = FeedbackFactory.create_research_feedback(
            feedback_text="测试反馈",
            research_id="research-123"
        )

        # 验证结果为 None
        self.assertIsNone(result)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_research_feedback(self, mock_feedback_manager):
        """测试获取研究反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock(spec=ResearchFeedbackDB)
        mock_db_object.id = uuid4()
        mock_db_object.feedback_text = "研究反馈"
        mock_db_object.accuracy_rating = 8.5
        mock_db_object.completeness_rating = 7.0
        mock_db_object.feedback_metadata = {"suggested_improvements": ["改进1", "改进2"]}
        mock_db_object.feedback_source = "human"

        mock_feedback_manager.get_feedback_by_id.return_value = mock_db_object

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.get_research_feedback(feedback_id)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ResearchFeedback)
        self.assertEqual(result.feedback_text, mock_db_object.feedback_text)
        self.assertEqual(result.accuracy_rating, mock_db_object.accuracy_rating)
        self.assertEqual(result.completeness_rating, mock_db_object.completeness_rating)
        self.assertEqual(result.suggested_improvements, mock_db_object.feedback_metadata["suggested_improvements"])
        self.assertEqual(result.feedback_source, mock_db_object.feedback_source)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.get_feedback_by_id.assert_called_once_with(feedback_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_content_feedback(self, mock_feedback_manager):
        """测试获取内容反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock(spec=ContentFeedbackDB)
        mock_db_object.id = uuid4()
        mock_db_object.content_id = "article-456"
        mock_db_object.feedback_text = "内容反馈"
        mock_db_object.rating = 8.0
        mock_db_object.feedback_metadata = {"feedback_categories": ["类别1", "类别2"]}
        mock_db_object.created_at = datetime.now(UTC)
        mock_db_object.user_id = "user-789"

        mock_feedback_manager.get_feedback_by_id.return_value = mock_db_object

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.get_content_feedback(feedback_id)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ContentFeedback)
        self.assertEqual(result.content_id, mock_db_object.content_id)
        self.assertEqual(result.feedback_text, mock_db_object.feedback_text)
        self.assertEqual(result.rating, mock_db_object.rating)
        self.assertEqual(result.feedback_categories, mock_db_object.feedback_metadata["feedback_categories"])
        self.assertEqual(result.created_at, mock_db_object.created_at)
        self.assertEqual(result.user_id, mock_db_object.user_id)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.get_feedback_by_id.assert_called_once_with(feedback_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_feedback_not_found(self, mock_feedback_manager):
        """测试获取不存在的反馈"""
        # 模拟 FeedbackManager 返回 None 表示未找到记录
        mock_feedback_manager.get_feedback_by_id.return_value = None

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.get_research_feedback(feedback_id)

        # 验证结果为 None
        self.assertIsNone(result)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_feedback_wrong_type(self, mock_feedback_manager):
        """测试获取错误类型的反馈"""
        # 模拟 FeedbackManager 返回错误类型的记录
        mock_db_object = MagicMock(spec=ContentFeedbackDB)
        mock_feedback_manager.get_feedback_by_id.return_value = mock_db_object

        # 执行方法 - 尝试获取研究反馈，但返回的是内容反馈
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.get_research_feedback(feedback_id)

        # 验证结果为 None
        self.assertIsNone(result)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_feedback_by_content_id(self, mock_feedback_manager):
        """测试获取特定内容的所有反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object1 = MagicMock(spec=ContentFeedbackDB)
        mock_db_object1.content_id = "article-123"
        mock_db_object1.feedback_text = "反馈1"
        mock_db_object1.rating = 8.0
        mock_db_object1.feedback_metadata = {"feedback_categories": ["类别1"]}
        mock_db_object1.created_at = datetime.now(UTC)
        mock_db_object1.user_id = "user-1"

        mock_db_object2 = MagicMock(spec=ContentFeedbackDB)
        mock_db_object2.content_id = "article-123"
        mock_db_object2.feedback_text = "反馈2"
        mock_db_object2.rating = 9.0
        mock_db_object2.feedback_metadata = {"feedback_categories": ["类别2"]}
        mock_db_object2.created_at = datetime.now(UTC)
        mock_db_object2.user_id = "user-2"

        mock_feedback_manager.get_feedback_by_content_id.return_value = [mock_db_object1, mock_db_object2]

        # 执行方法
        content_id = "article-123"
        result = FeedbackFactory.get_feedback_by_content_id(content_id)

        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ContentFeedback)
        self.assertIsInstance(result[1], ContentFeedback)
        self.assertEqual(result[0].feedback_text, "反馈1")
        self.assertEqual(result[1].feedback_text, "反馈2")

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.get_feedback_by_content_id.assert_called_once_with(content_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_get_feedback_by_research_id(self, mock_feedback_manager):
        """测试获取特定研究的所有反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object1 = MagicMock(spec=ResearchFeedbackDB)
        mock_db_object1.feedback_text = "研究反馈1"
        mock_db_object1.accuracy_rating = 8.0
        mock_db_object1.completeness_rating = 7.0
        mock_db_object1.feedback_metadata = {"suggested_improvements": ["改进1"]}
        mock_db_object1.feedback_source = "human"

        mock_db_object2 = MagicMock(spec=ResearchFeedbackDB)
        mock_db_object2.feedback_text = "研究反馈2"
        mock_db_object2.accuracy_rating = 9.0
        mock_db_object2.completeness_rating = 8.0
        mock_db_object2.feedback_metadata = {"suggested_improvements": ["改进2"]}
        mock_db_object2.feedback_source = "system"

        mock_feedback_manager.get_feedback_by_research_id.return_value = [mock_db_object1, mock_db_object2]

        # 执行方法
        research_id = "research-123"
        result = FeedbackFactory.get_feedback_by_research_id(research_id)

        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ResearchFeedback)
        self.assertIsInstance(result[1], ResearchFeedback)
        self.assertEqual(result[0].feedback_text, "研究反馈1")
        self.assertEqual(result[1].feedback_text, "研究反馈2")

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.get_feedback_by_research_id.assert_called_once_with(research_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_update_research_feedback(self, mock_feedback_manager):
        """测试更新研究反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock()
        mock_feedback_manager.update_feedback.return_value = mock_db_object

        # 创建要更新的反馈对象
        feedback = ResearchFeedback(
            feedback_text="更新后的研究反馈",
            accuracy_rating=9.0,
            completeness_rating=8.0,
            suggested_improvements=["新的改进建议"],
            feedback_source="human"
        )

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.update_research_feedback(feedback_id, feedback)

        # 验证结果
        self.assertTrue(result)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.update_feedback.assert_called_once()
        call_args = mock_feedback_manager.update_feedback.call_args
        self.assertEqual(call_args[0][0], feedback_id)  # 检查 feedback_id
        updates = call_args[0][1]  # 获取 updates 字典

        # 检查更新包含预期的字段
        self.assertEqual(updates["feedback_text"], "更新后的研究反馈")
        self.assertEqual(updates["accuracy_rating"], 9.0)
        self.assertEqual(updates["completeness_rating"], 8.0)
        self.assertEqual(updates["suggested_improvements"], ["新的改进建议"])
        self.assertEqual(updates["feedback_source"], "human")

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_update_content_feedback(self, mock_feedback_manager):
        """测试更新内容反馈"""
        # 模拟 FeedbackManager 响应
        mock_db_object = MagicMock()
        mock_feedback_manager.update_feedback.return_value = mock_db_object

        # 创建要更新的反馈对象
        feedback = ContentFeedback(
            content_id="article-123",
            feedback_text="更新后的内容反馈",
            rating=9.5,
            feedback_categories=["新类别1", "新类别2"],
            user_id="user-456"
        )

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.update_content_feedback(feedback_id, feedback)

        # 验证结果
        self.assertTrue(result)

        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.update_feedback.assert_called_once()
        call_args = mock_feedback_manager.update_feedback.call_args
        self.assertEqual(call_args[0][0], feedback_id)  # 检查 feedback_id
        updates = call_args[0][1]  # 获取 updates 字典

        # 检查更新包含预期的字段
        self.assertEqual(updates["content_id"], "article-123")
        self.assertEqual(updates["feedback_text"], "更新后的内容反馈")
        self.assertEqual(updates["rating"], 9.5)
        self.assertEqual(updates["feedback_categories"], ["新类别1", "新类别2"])
        self.assertEqual(updates["user_id"], "user-456")

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_update_feedback_db_failure(self, mock_feedback_manager):
        """测试更新反馈时数据库失败"""
        # 模拟 FeedbackManager 返回 None 表示数据库操作失败
        mock_feedback_manager.update_feedback.return_value = None

        # 创建要更新的反馈对象
        feedback = ResearchFeedback(feedback_text="测试反馈")

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.update_research_feedback(feedback_id, feedback)

        # 验证结果为 False
        self.assertFalse(result)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_delete_feedback(self, mock_feedback_manager):
        """测试删除反馈"""
        # 模拟 FeedbackManager 响应
        mock_feedback_manager.delete_feedback.return_value = True

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.delete_feedback(feedback_id)

        # 验证结果
        self.assertTrue(result)
        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.delete_feedback.assert_called_once_with(feedback_id)

    @patch('core.models.feedback.feedback_factory.FeedbackManager')
    def test_delete_feedback_failure(self, mock_feedback_manager):
        """测试删除反馈失败"""
        # 模拟 FeedbackManager 响应
        mock_feedback_manager.delete_feedback.return_value = False

        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = FeedbackFactory.delete_feedback(feedback_id)

        # 验证结果
        self.assertFalse(result)
        # 验证与 FeedbackManager 的交互
        mock_feedback_manager.delete_feedback.assert_called_once_with(feedback_id)

if __name__ == "__main__":
    unittest.main()
