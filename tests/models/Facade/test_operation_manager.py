"""测试 OperationManager 类的功能"""
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID

from core.models.facade import OperationManager
from core.models.feedback import ResearchFeedback, ContentFeedback
from core.models.progress import ArticleProductionProgress

class TestOperationManager(unittest.TestCase):
    """测试 OperationManager 类"""

    def setUp(self):
        """测试前初始化"""
        pass

    def tearDown(self):
        """测试后清理"""
        pass

    @patch('core.models.feedback.feedback_manager.FeedbackManager')
    @patch('core.models.progress.progress_manager.ProgressManager')
    def test_initialize(self, mock_progress_manager, mock_feedback_manager):
        """测试初始化方法"""
        # 执行初始化
        OperationManager.initialize(use_db=True)
        
        # 验证子系统初始化
        mock_feedback_manager.initialize.assert_called_once_with(use_db=True)
        mock_progress_manager.initialize.assert_called_once_with(use_db=True)

    #
    # 进度相关测试
    #
    
    @patch('core.models.operations.operation_manager.ProgressFactory')
    def test_create_progress(self, mock_progress_factory):
        """测试创建进度"""
        # 模拟 ProgressFactory 响应
        mock_progress = MagicMock(spec=ArticleProductionProgress)
        mock_progress_factory.create_progress.return_value = mock_progress
        
        # 执行方法
        entity_id = "article-123"
        operation_type = "article_production"
        result = OperationManager.create_progress(entity_id, operation_type)
        
        # 验证结果
        self.assertEqual(result, mock_progress)
        mock_progress_factory.create_progress.assert_called_once_with(entity_id=entity_id, operation_type=operation_type)
    
    @patch('core.models.operations.operation_manager.ProgressFactory')
    def test_get_progress(self, mock_progress_factory):
        """测试获取进度"""
        # 模拟 ProgressFactory 响应
        mock_progress = MagicMock(spec=ArticleProductionProgress)
        mock_progress_factory.get_progress.return_value = mock_progress
        
        # 执行方法
        progress_id = uuid4()
        result = OperationManager.get_progress(progress_id)
        
        # 验证结果
        self.assertEqual(result, mock_progress)
        mock_progress_factory.get_progress.assert_called_once_with(progress_id)
    
    @patch('core.models.operations.operation_manager.ProgressFactory')
    def test_update_progress(self, mock_progress_factory):
        """测试更新进度"""
        # 模拟 ProgressFactory 响应
        mock_progress_factory.update_progress.return_value = True
        
        # 执行方法
        progress_id = uuid4()
        progress_instance = MagicMock(spec=ArticleProductionProgress)
        result = OperationManager.update_progress(progress_id, progress_instance)
        
        # 验证结果
        self.assertTrue(result)
        mock_progress_factory.update_progress.assert_called_once_with(progress_id, progress_instance)
    
    @patch('core.models.operations.operation_manager.ProgressFactory')
    def test_delete_progress(self, mock_progress_factory):
        """测试删除进度"""
        # 模拟 ProgressFactory 响应
        mock_progress_factory.delete_progress.return_value = True
        
        # 执行方法
        progress_id = uuid4()
        result = OperationManager.delete_progress(progress_id)
        
        # 验证结果
        self.assertTrue(result)
        mock_progress_factory.delete_progress.assert_called_once_with(progress_id)
    
    #
    # 反馈相关测试
    #
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_create_research_feedback(self, mock_feedback_factory):
        """测试创建研究反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback = MagicMock(spec=ResearchFeedback)
        mock_feedback_factory.create_research_feedback.return_value = mock_feedback
        
        # 执行方法
        feedback_text = "研究结果很全面，但缺少一些关键数据"
        research_id = "research-123"
        accuracy_rating = 8.5
        completeness_rating = 7.0
        suggested_improvements = ["添加更多数据来源", "增加图表展示"]
        feedback_source = "human"
        
        result = OperationManager.create_research_feedback(
            feedback_text=feedback_text,
            research_id=research_id,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            suggested_improvements=suggested_improvements,
            feedback_source=feedback_source
        )
        
        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_feedback_factory.create_research_feedback.assert_called_once_with(
            feedback_text=feedback_text,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            suggested_improvements=suggested_improvements,
            feedback_source=feedback_source,
            research_id=research_id
        )
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_create_content_feedback(self, mock_feedback_factory):
        """测试创建内容反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback = MagicMock(spec=ContentFeedback)
        mock_feedback_factory.create_content_feedback.return_value = mock_feedback
        
        # 执行方法
        content_id = "article-456"
        feedback_text = "文章结构清晰，但有些表述不够准确"
        rating = 8.0
        feedback_categories = ["clarity", "accuracy"]
        user_id = "user-789"
        
        result = OperationManager.create_content_feedback(
            content_id=content_id,
            feedback_text=feedback_text,
            rating=rating,
            feedback_categories=feedback_categories,
            user_id=user_id
        )
        
        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_feedback_factory.create_content_feedback.assert_called_once_with(
            content_id=content_id,
            feedback_text=feedback_text,
            rating=rating,
            feedback_categories=feedback_categories,
            user_id=user_id
        )
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_get_research_feedback(self, mock_feedback_factory):
        """测试获取研究反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback = MagicMock(spec=ResearchFeedback)
        mock_feedback_factory.get_research_feedback.return_value = mock_feedback
        
        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = OperationManager.get_research_feedback(feedback_id)
        
        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_feedback_factory.get_research_feedback.assert_called_once_with(feedback_id)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_get_content_feedback(self, mock_feedback_factory):
        """测试获取内容反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback = MagicMock(spec=ContentFeedback)
        mock_feedback_factory.get_content_feedback.return_value = mock_feedback
        
        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = OperationManager.get_content_feedback(feedback_id)
        
        # 验证结果
        self.assertEqual(result, mock_feedback)
        mock_feedback_factory.get_content_feedback.assert_called_once_with(feedback_id)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_get_feedback_by_content_id(self, mock_feedback_factory):
        """测试获取内容的所有反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedbacks = [MagicMock(spec=ContentFeedback), MagicMock(spec=ContentFeedback)]
        mock_feedback_factory.get_feedback_by_content_id.return_value = mock_feedbacks
        
        # 执行方法
        content_id = "article-123"
        result = OperationManager.get_feedback_by_content_id(content_id)
        
        # 验证结果
        self.assertEqual(result, mock_feedbacks)
        mock_feedback_factory.get_feedback_by_content_id.assert_called_once_with(content_id)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_get_feedback_by_research_id(self, mock_feedback_factory):
        """测试获取研究的所有反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedbacks = [MagicMock(spec=ResearchFeedback), MagicMock(spec=ResearchFeedback)]
        mock_feedback_factory.get_feedback_by_research_id.return_value = mock_feedbacks
        
        # 执行方法
        research_id = "research-123"
        result = OperationManager.get_feedback_by_research_id(research_id)
        
        # 验证结果
        self.assertEqual(result, mock_feedbacks)
        mock_feedback_factory.get_feedback_by_research_id.assert_called_once_with(research_id)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_update_research_feedback(self, mock_feedback_factory):
        """测试更新研究反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback_factory.update_research_feedback.return_value = True
        
        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        feedback = MagicMock(spec=ResearchFeedback)
        result = OperationManager.update_research_feedback(feedback_id, feedback)
        
        # 验证结果
        self.assertTrue(result)
        mock_feedback_factory.update_research_feedback.assert_called_once_with(feedback_id, feedback)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_update_content_feedback(self, mock_feedback_factory):
        """测试更新内容反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback_factory.update_content_feedback.return_value = True
        
        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        feedback = MagicMock(spec=ContentFeedback)
        result = OperationManager.update_content_feedback(feedback_id, feedback)
        
        # 验证结果
        self.assertTrue(result)
        mock_feedback_factory.update_content_feedback.assert_called_once_with(feedback_id, feedback)
    
    @patch('core.models.operations.operation_manager.FeedbackFactory')
    def test_delete_feedback(self, mock_feedback_factory):
        """测试删除反馈"""
        # 模拟 FeedbackFactory 响应
        mock_feedback_factory.delete_feedback.return_value = True
        
        # 执行方法
        feedback_id = UUID('12345678-1234-5678-1234-567812345678')
        result = OperationManager.delete_feedback(feedback_id)
        
        # 验证结果
        self.assertTrue(result)
        mock_feedback_factory.delete_feedback.assert_called_once_with(feedback_id)

if __name__ == "__main__":
    unittest.main()
