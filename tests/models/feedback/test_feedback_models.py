"""测试反馈模型的基本功能"""
import unittest
from datetime import datetime, UTC
from uuid import uuid4

from core.models.feedback.feedback import ResearchFeedback, ContentFeedback

class TestResearchFeedback(unittest.TestCase):
    """测试 ResearchFeedback 类"""

    def setUp(self):
        """测试前初始化"""
        self.feedback_text = "研究结果很全面，但缺少一些关键数据"
        self.accuracy_rating = 8.5
        self.completeness_rating = 7.0
        self.suggested_improvements = ["添加更多数据来源", "增加图表展示"]
        self.feedback_source = "human"

        self.feedback = ResearchFeedback(
            feedback_text=self.feedback_text,
            accuracy_rating=self.accuracy_rating,
            completeness_rating=self.completeness_rating,
            suggested_improvements=self.suggested_improvements,
            feedback_source=self.feedback_source
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.feedback.feedback_text, self.feedback_text)
        self.assertEqual(self.feedback.accuracy_rating, self.accuracy_rating)
        self.assertEqual(self.feedback.completeness_rating, self.completeness_rating)
        self.assertEqual(self.feedback.suggested_improvements, self.suggested_improvements)
        self.assertEqual(self.feedback.feedback_source, self.feedback_source)

    def test_to_dict(self):
        """测试转换为字典"""
        feedback_dict = self.feedback.to_dict()
        
        self.assertEqual(feedback_dict["feedback_text"], self.feedback_text)
        self.assertEqual(feedback_dict["accuracy_rating"], self.accuracy_rating)
        self.assertEqual(feedback_dict["completeness_rating"], self.completeness_rating)
        self.assertEqual(feedback_dict["suggested_improvements"], self.suggested_improvements)
        self.assertEqual(feedback_dict["feedback_source"], self.feedback_source)

    def test_from_dict(self):
        """测试从字典创建"""
        feedback_dict = {
            "feedback_text": self.feedback_text,
            "accuracy_rating": self.accuracy_rating,
            "completeness_rating": self.completeness_rating,
            "suggested_improvements": self.suggested_improvements,
            "feedback_source": self.feedback_source
        }
        
        feedback = ResearchFeedback.from_dict(feedback_dict)
        
        self.assertEqual(feedback.feedback_text, self.feedback_text)
        self.assertEqual(feedback.accuracy_rating, self.accuracy_rating)
        self.assertEqual(feedback.completeness_rating, self.completeness_rating)
        self.assertEqual(feedback.suggested_improvements, self.suggested_improvements)
        self.assertEqual(feedback.feedback_source, self.feedback_source)

    def test_default_values(self):
        """测试默认值"""
        feedback = ResearchFeedback(feedback_text="简单反馈")
        
        self.assertEqual(feedback.feedback_text, "简单反馈")
        self.assertIsNone(feedback.accuracy_rating)
        self.assertIsNone(feedback.completeness_rating)
        self.assertEqual(feedback.suggested_improvements, [])
        self.assertEqual(feedback.feedback_source, "system")

class TestContentFeedback(unittest.TestCase):
    """测试 ContentFeedback 类"""

    def setUp(self):
        """测试前初始化"""
        self.content_id = "article-456"
        self.feedback_text = "文章结构清晰，但有些表述不够准确"
        self.rating = 8.0
        self.feedback_categories = ["clarity", "accuracy"]
        self.user_id = "user-789"
        self.created_at = datetime.now(UTC)

        self.feedback = ContentFeedback(
            content_id=self.content_id,
            feedback_text=self.feedback_text,
            rating=self.rating,
            feedback_categories=self.feedback_categories,
            created_at=self.created_at,
            user_id=self.user_id
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.feedback.content_id, self.content_id)
        self.assertEqual(self.feedback.feedback_text, self.feedback_text)
        self.assertEqual(self.feedback.rating, self.rating)
        self.assertEqual(self.feedback.feedback_categories, self.feedback_categories)
        self.assertEqual(self.feedback.created_at, self.created_at)
        self.assertEqual(self.feedback.user_id, self.user_id)

    def test_to_dict(self):
        """测试转换为字典"""
        feedback_dict = self.feedback.to_dict()
        
        self.assertEqual(feedback_dict["content_id"], self.content_id)
        self.assertEqual(feedback_dict["feedback_text"], self.feedback_text)
        self.assertEqual(feedback_dict["rating"], self.rating)
        self.assertEqual(feedback_dict["feedback_categories"], self.feedback_categories)
        self.assertEqual(feedback_dict["created_at"], self.created_at.isoformat())
        self.assertEqual(feedback_dict["user_id"], self.user_id)

    def test_from_dict(self):
        """测试从字典创建"""
        feedback_dict = {
            "content_id": self.content_id,
            "feedback_text": self.feedback_text,
            "rating": self.rating,
            "feedback_categories": self.feedback_categories,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id
        }
        
        feedback = ContentFeedback.from_dict(feedback_dict)
        
        self.assertEqual(feedback.content_id, self.content_id)
        self.assertEqual(feedback.feedback_text, self.feedback_text)
        self.assertEqual(feedback.rating, self.rating)
        self.assertEqual(feedback.feedback_categories, self.feedback_categories)
        # 检查 created_at 是否正确解析
        self.assertIsInstance(feedback.created_at, datetime)
        self.assertEqual(feedback.user_id, self.user_id)

    def test_default_values(self):
        """测试默认值"""
        feedback = ContentFeedback(
            content_id="article-123",
            feedback_text="简单反馈"
        )
        
        self.assertEqual(feedback.content_id, "article-123")
        self.assertEqual(feedback.feedback_text, "简单反馈")
        self.assertIsNone(feedback.rating)
        self.assertEqual(feedback.feedback_categories, [])
        self.assertIsInstance(feedback.created_at, datetime)
        self.assertIsNone(feedback.user_id)

if __name__ == "__main__":
    unittest.main()
