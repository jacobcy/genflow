"""操作管理器

为反馈和进度模块提供统一的门面（Facade）接口。
简化客户端与这些子系统的交互。
"""
from typing import Optional, Dict, Any, List, Union
from uuid import UUID
from loguru import logger

from ..feedback import FeedbackFactory, ResearchFeedback, ContentFeedback
from ..progress import ArticleProductionProgress
from ..progress.progress_factory import ProgressFactory

class OperationManager:
    """操作管理器

    为反馈和进度模块提供统一的门面（Facade）接口。
    简化客户端与这些子系统的交互。
    """

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化操作管理器

        Args:
            use_db: 是否使用数据库
        """
        # 初始化各个子系统
        from ..feedback.feedback_manager import FeedbackManager
        from ..progress.progress_manager import ProgressManager

        FeedbackManager.initialize(use_db=use_db)
        ProgressManager.initialize(use_db=use_db)

        logger.info("操作管理器已初始化")

    #
    # 进度相关操作
    #

    @classmethod
    def create_progress(cls, entity_id: str, operation_type: str) -> Optional[ArticleProductionProgress]:
        """创建进度

        Args:
            entity_id: 实体ID
            operation_type: 操作类型

        Returns:
            创建的进度对象或 None
        """
        return ProgressFactory.create_progress(entity_id=entity_id, operation_type=operation_type)

    @classmethod
    def get_progress(cls, progress_id: UUID) -> Optional[ArticleProductionProgress]:
        """获取进度

        Args:
            progress_id: 进度ID

        Returns:
            进度对象或 None
        """
        return ProgressFactory.get_progress(progress_id)

    @classmethod
    def update_progress(cls, progress_id: UUID, progress_instance: ArticleProductionProgress) -> bool:
        """更新进度

        Args:
            progress_id: 进度ID
            progress_instance: 进度实例

        Returns:
            是否成功
        """
        return ProgressFactory.update_progress(progress_id, progress_instance)

    @classmethod
    def delete_progress(cls, progress_id: UUID) -> bool:
        """删除进度

        Args:
            progress_id: 进度ID

        Returns:
            是否成功
        """
        return ProgressFactory.delete_progress(progress_id)

    #
    # 反馈相关操作
    #

    @classmethod
    def create_research_feedback(cls,
                               feedback_text: str,
                               research_id: Optional[str] = None,
                               accuracy_rating: Optional[float] = None,
                               completeness_rating: Optional[float] = None,
                               suggested_improvements: List[str] = None,  # type: ignore
                               feedback_source: str = "system") -> Optional[ResearchFeedback]:
        """创建研究反馈

        Args:
            feedback_text: 反馈文本
            research_id: 研究ID
            accuracy_rating: 准确性评分
            completeness_rating: 完整性评分
            suggested_improvements: 建议改进
            feedback_source: 反馈来源

        Returns:
            创建的反馈对象或 None
        """
        return FeedbackFactory.create_research_feedback(
            feedback_text=feedback_text,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            suggested_improvements=suggested_improvements,
            feedback_source=feedback_source,
            research_id=research_id
        )

    @classmethod
    def create_content_feedback(cls,
                              content_id: str,
                              feedback_text: str,
                              rating: Optional[float] = None,
                              feedback_categories: List[str] = None,  # type: ignore
                              user_id: Optional[str] = None) -> Optional[ContentFeedback]:
        """创建内容反馈

        Args:
            content_id: 内容ID
            feedback_text: 反馈文本
            rating: 评分
            feedback_categories: 反馈类别
            user_id: 用户ID

        Returns:
            创建的反馈对象或 None
        """
        return FeedbackFactory.create_content_feedback(
            content_id=content_id,
            feedback_text=feedback_text,
            rating=rating,
            feedback_categories=feedback_categories,
            user_id=user_id
        )

    @classmethod
    def get_research_feedback(cls, feedback_id: UUID) -> Optional[ResearchFeedback]:
        """获取研究反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            反馈对象或 None
        """
        return FeedbackFactory.get_research_feedback(feedback_id)

    @classmethod
    def get_content_feedback(cls, feedback_id: UUID) -> Optional[ContentFeedback]:
        """获取内容反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            反馈对象或 None
        """
        return FeedbackFactory.get_content_feedback(feedback_id)

    @classmethod
    def get_feedback_by_content_id(cls, content_id: str) -> List[ContentFeedback]:
        """获取内容的所有反馈

        Args:
            content_id: 内容ID

        Returns:
            反馈对象列表
        """
        return FeedbackFactory.get_feedback_by_content_id(content_id)

    @classmethod
    def get_feedback_by_research_id(cls, research_id: str) -> List[ResearchFeedback]:
        """获取研究的所有反馈

        Args:
            research_id: 研究ID

        Returns:
            反馈对象列表
        """
        return FeedbackFactory.get_feedback_by_research_id(research_id)

    @classmethod
    def update_research_feedback(cls, feedback_id: UUID, feedback: ResearchFeedback) -> bool:
        """更新研究反馈

        Args:
            feedback_id: 反馈ID
            feedback: 更新后的反馈对象

        Returns:
            是否成功
        """
        return FeedbackFactory.update_research_feedback(feedback_id, feedback)

    @classmethod
    def update_content_feedback(cls, feedback_id: UUID, feedback: ContentFeedback) -> bool:
        """更新内容反馈

        Args:
            feedback_id: 反馈ID
            feedback: 更新后的反馈对象

        Returns:
            是否成功
        """
        return FeedbackFactory.update_content_feedback(feedback_id, feedback)

    @classmethod
    def delete_feedback(cls, feedback_id: UUID) -> bool:
        """删除反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            是否成功
        """
        return FeedbackFactory.delete_feedback(feedback_id)
