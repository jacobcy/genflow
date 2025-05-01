"""反馈工厂

负责创建、获取和更新不同类型的反馈对象。
协调 FeedbackManager 进行持久化。
"""
from typing import Optional, Any, Dict, List
from uuid import UUID
from loguru import logger
from datetime import datetime, UTC

from .feedback_manager import FeedbackManager
from .feedback import ResearchFeedback, ContentFeedback
from .feedback_db import FeedbackDB, ResearchFeedbackDB, ContentFeedbackDB

class FeedbackFactory:
    """反馈工厂

    负责创建、获取和更新不同类型的反馈对象。
    协调 FeedbackManager 进行持久化。
    """

    @classmethod
    def create_research_feedback(cls,
                                feedback_text: str,
                                accuracy_rating: Optional[float] = None,
                                completeness_rating: Optional[float] = None,
                                suggested_improvements: List[str] = None,  # type: ignore
                                feedback_source: str = "system",
                                research_id: Optional[str] = None) -> Optional[ResearchFeedback]:
        """创建并持久化研究反馈

        Args:
            feedback_text: 反馈文本
            accuracy_rating: 准确性评分 (1-10)
            completeness_rating: 完整性评分 (1-10)
            suggested_improvements: 建议改进列表
            feedback_source: 反馈来源 ('system' 或 'human')
            research_id: 关联的研究ID

        Returns:
            创建的 ResearchFeedback 对象或 None
        """
        # 创建业务逻辑对象
        feedback = ResearchFeedback(
            feedback_text=feedback_text,
            accuracy_rating=accuracy_rating,
            completeness_rating=completeness_rating,
            suggested_improvements=suggested_improvements or [],
            feedback_source=feedback_source
        )

        # 准备持久化数据
        data = feedback.to_dict()
        data["research_id"] = research_id

        # 持久化到数据库
        feedback_db = FeedbackManager.create_feedback("research", data)
        if not feedback_db:
            logger.error("创建研究反馈失败")
            return None

        # 返回业务逻辑对象
        return feedback

    @classmethod
    def create_content_feedback(cls,
                               content_id: str,
                               feedback_text: str,
                               rating: Optional[float] = None,
                               feedback_categories: List[str] = None,  # type: ignore
                               user_id: Optional[str] = None) -> Optional[ContentFeedback]:
        """创建并持久化内容反馈

        Args:
            content_id: 内容ID
            feedback_text: 反馈文本
            rating: 评分 (1-10)
            feedback_categories: 反馈类别列表
            user_id: 用户ID

        Returns:
            创建的 ContentFeedback 对象或 None
        """
        # 创建业务逻辑对象
        feedback = ContentFeedback(
            content_id=content_id,
            feedback_text=feedback_text,
            rating=rating,
            feedback_categories=feedback_categories or [],
            created_at=datetime.now(UTC),
            user_id=user_id
        )

        # 准备持久化数据
        data = feedback.to_dict()
        # 转换 datetime 为 ISO 格式字符串
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        # 持久化到数据库
        feedback_db = FeedbackManager.create_feedback("content", data)
        if not feedback_db:
            logger.error("创建内容反馈失败")
            return None

        # 返回业务逻辑对象
        return feedback

    @classmethod
    def get_research_feedback(cls, feedback_id: UUID) -> Optional[ResearchFeedback]:
        """获取研究反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            ResearchFeedback 对象或 None
        """
        # 从数据库获取
        feedback_db = FeedbackManager.get_feedback_by_id(feedback_id)
        if not feedback_db or not isinstance(feedback_db, ResearchFeedbackDB):
            return None

        # 转换为业务逻辑对象
        suggested_improvements = feedback_db.feedback_metadata.get("suggested_improvements", []) if feedback_db.feedback_metadata else []

        return ResearchFeedback(
            feedback_text=feedback_db.feedback_text,
            accuracy_rating=feedback_db.accuracy_rating,
            completeness_rating=feedback_db.completeness_rating,
            suggested_improvements=suggested_improvements,
            feedback_source=feedback_db.feedback_source
        )

    @classmethod
    def get_content_feedback(cls, feedback_id: UUID) -> Optional[ContentFeedback]:
        """获取内容反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            ContentFeedback 对象或 None
        """
        # 从数据库获取
        feedback_db = FeedbackManager.get_feedback_by_id(feedback_id)
        if not feedback_db or not isinstance(feedback_db, ContentFeedbackDB):
            return None

        # 转换为业务逻辑对象
        feedback_categories = feedback_db.feedback_metadata.get("feedback_categories", []) if feedback_db.feedback_metadata else []

        return ContentFeedback(
            content_id=feedback_db.content_id,
            feedback_text=feedback_db.feedback_text,
            rating=feedback_db.rating,
            feedback_categories=feedback_categories,
            created_at=feedback_db.created_at,
            user_id=feedback_db.user_id
        )

    @classmethod
    def get_feedback_by_content_id(cls, content_id: str) -> List[ContentFeedback]:
        """获取特定内容的所有反馈

        Args:
            content_id: 内容ID

        Returns:
            ContentFeedback 对象列表
        """
        # 从数据库获取
        feedback_dbs = FeedbackManager.get_feedback_by_content_id(content_id)

        # 转换为业务逻辑对象
        result = []
        for feedback_db in feedback_dbs:
            feedback_categories = feedback_db.feedback_metadata.get("feedback_categories", []) if feedback_db.feedback_metadata else []

            result.append(ContentFeedback(
                content_id=feedback_db.content_id,
                feedback_text=feedback_db.feedback_text,
                rating=feedback_db.rating,
                feedback_categories=feedback_categories,
                created_at=feedback_db.created_at,
                user_id=feedback_db.user_id
            ))

        return result

    @classmethod
    def get_feedback_by_research_id(cls, research_id: str) -> List[ResearchFeedback]:
        """获取特定研究的所有反馈

        Args:
            research_id: 研究ID

        Returns:
            ResearchFeedback 对象列表
        """
        # 从数据库获取
        feedback_dbs = FeedbackManager.get_feedback_by_research_id(research_id)

        # 转换为业务逻辑对象
        result = []
        for feedback_db in feedback_dbs:
            suggested_improvements = feedback_db.feedback_metadata.get("suggested_improvements", []) if feedback_db.feedback_metadata else []

            result.append(ResearchFeedback(
                feedback_text=feedback_db.feedback_text,
                accuracy_rating=feedback_db.accuracy_rating,
                completeness_rating=feedback_db.completeness_rating,
                suggested_improvements=suggested_improvements,
                feedback_source=feedback_db.feedback_source
            ))

        return result

    @classmethod
    def update_research_feedback(cls, feedback_id: UUID, feedback: ResearchFeedback) -> bool:
        """更新研究反馈

        Args:
            feedback_id: 反馈ID
            feedback: 更新后的 ResearchFeedback 对象

        Returns:
            是否更新成功
        """
        # 准备更新数据
        updates = feedback.to_dict()

        # 更新数据库
        result = FeedbackManager.update_feedback(feedback_id, updates)
        return result is not None

    @classmethod
    def update_content_feedback(cls, feedback_id: UUID, feedback: ContentFeedback) -> bool:
        """更新内容反馈

        Args:
            feedback_id: 反馈ID
            feedback: 更新后的 ContentFeedback 对象

        Returns:
            是否更新成功
        """
        # 准备更新数据
        updates = feedback.to_dict()

        # 转换 datetime 为 Python datetime 对象
        if "created_at" in updates and isinstance(updates["created_at"], str):
            updates["created_at"] = datetime.fromisoformat(updates["created_at"])

        # 更新数据库
        result = FeedbackManager.update_feedback(feedback_id, updates)
        return result is not None

    @classmethod
    def delete_feedback(cls, feedback_id: UUID) -> bool:
        """删除反馈

        Args:
            feedback_id: 反馈ID

        Returns:
            是否删除成功
        """
        return FeedbackManager.delete_feedback(feedback_id)
