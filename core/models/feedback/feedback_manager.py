"""反馈管理器

负责反馈数据的数据库 CRUD 操作。
"""
from typing import Optional, Dict, Any, List
from uuid import UUID
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from ..infra.base_manager import BaseManager
from .feedback_db import FeedbackDB, ResearchFeedbackDB, ContentFeedbackDB
from ..db.session import get_db

class FeedbackManager(BaseManager):
    """反馈管理器

    负责反馈数据的数据库 CRUD 操作。
    """

    @classmethod
    def create_feedback(cls, feedback_type: str, data: Dict[str, Any]) -> Optional[FeedbackDB]:
        """创建新的反馈记录

        Args:
            feedback_type: 反馈类型 ('research' 或 'content')
            data: 反馈数据

        Returns:
            创建的 FeedbackDB 对象或 None (如果出错)
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法创建反馈记录")
            return None

        try:
            with get_db() as db:
                if feedback_type == "research":
                    # 提取特定字段
                    accuracy_rating = data.pop("accuracy_rating", None)
                    completeness_rating = data.pop("completeness_rating", None)
                    research_id = data.pop("research_id", None)
                    suggested_improvements = data.pop("suggested_improvements", [])

                    # 创建研究反馈
                    feedback = ResearchFeedbackDB(
                        accuracy_rating=accuracy_rating,
                        completeness_rating=completeness_rating,
                        research_id=research_id,
                        feedback_metadata={"suggested_improvements": suggested_improvements},
                        **data
                    )
                elif feedback_type == "content":
                    # 提取特定字段
                    content_id = data.pop("content_id")
                    user_id = data.pop("user_id", None)
                    feedback_categories = data.pop("feedback_categories", [])

                    # 创建内容反馈
                    feedback = ContentFeedbackDB(
                        content_id=content_id,
                        user_id=user_id,
                        feedback_metadata={"feedback_categories": feedback_categories},
                        **data
                    )
                else:
                    logger.error(f"不支持的反馈类型: {feedback_type}")
                    return None

                db.add(feedback)
                db.commit()
                db.refresh(feedback)

                logger.info(f"已创建 {feedback_type} 类型的反馈，ID: {feedback.id}")
                return feedback
        except SQLAlchemyError as e:
            logger.error(f"创建反馈记录失败: {e}")
            return None

    @classmethod
    def get_feedback_by_id(cls, feedback_id: UUID) -> Optional[FeedbackDB]:
        """通过ID获取反馈记录

        Args:
            feedback_id: 反馈记录的UUID

        Returns:
            FeedbackDB 对象或 None
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取反馈记录")
            return None

        try:
            with get_db() as db:
                return db.query(FeedbackDB).filter(FeedbackDB.id == feedback_id).first()
        except SQLAlchemyError as e:
            logger.error(f"获取反馈记录失败，ID {feedback_id}: {e}")
            return None

    @classmethod
    def get_feedback_by_content_id(cls, content_id: str) -> List[ContentFeedbackDB]:
        """获取特定内容的所有反馈

        Args:
            content_id: 内容ID

        Returns:
            ContentFeedbackDB 对象列表
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取内容反馈")
            return []

        try:
            with get_db() as db:
                return db.query(ContentFeedbackDB).filter(
                    ContentFeedbackDB.content_id == content_id
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"获取内容反馈失败，内容ID {content_id}: {e}")
            return []

    @classmethod
    def get_feedback_by_research_id(cls, research_id: str) -> List[ResearchFeedbackDB]:
        """获取特定研究的所有反馈

        Args:
            research_id: 研究ID

        Returns:
            ResearchFeedbackDB 对象列表
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取研究反馈")
            return []

        try:
            with get_db() as db:
                return db.query(ResearchFeedbackDB).filter(
                    ResearchFeedbackDB.research_id == research_id
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"获取研究反馈失败，研究ID {research_id}: {e}")
            return []

    @classmethod
    def update_feedback(cls, feedback_id: UUID, updates: Dict[str, Any]) -> Optional[FeedbackDB]:
        """更新反馈记录

        Args:
            feedback_id: 反馈记录的UUID
            updates: 包含要更新字段的字典

        Returns:
            更新后的 FeedbackDB 对象或 None (如果记录不存在或出错)
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法更新反馈记录")
            return None

        try:
            with get_db() as db:
                feedback = db.query(FeedbackDB).filter(FeedbackDB.id == feedback_id).first()
                if not feedback:
                    logger.warning(f"未找到要更新的反馈记录，ID {feedback_id}")
                    return None

                # 处理特殊字段
                if isinstance(feedback, ResearchFeedbackDB) and "suggested_improvements" in updates:
                    suggested_improvements = updates.pop("suggested_improvements")
                    if not feedback.feedback_metadata:
                        feedback.feedback_metadata = {}
                    feedback.feedback_metadata["suggested_improvements"] = suggested_improvements

                if isinstance(feedback, ContentFeedbackDB) and "feedback_categories" in updates:
                    feedback_categories = updates.pop("feedback_categories")
                    if not feedback.feedback_metadata:
                        feedback.feedback_metadata = {}
                    feedback.feedback_metadata["feedback_categories"] = feedback_categories

                # 更新普通字段
                for key, value in updates.items():
                    if hasattr(feedback, key):
                        setattr(feedback, key, value)
                    else:
                        logger.warning(f"尝试更新不存在的字段 '{key}'，反馈ID {feedback_id}")

                db.commit()
                db.refresh(feedback)

                logger.info(f"已更新反馈记录，ID: {feedback_id}")
                return feedback
        except SQLAlchemyError as e:
            logger.error(f"更新反馈记录失败，ID {feedback_id}: {e}")
            return None

    @classmethod
    def delete_feedback(cls, feedback_id: UUID) -> bool:
        """删除反馈记录

        Args:
            feedback_id: 反馈记录的UUID

        Returns:
            True 如果成功删除，False 如果记录不存在或出错
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法删除反馈记录")
            return False

        try:
            with get_db() as db:
                feedback = db.query(FeedbackDB).filter(FeedbackDB.id == feedback_id).first()
                if not feedback:
                    logger.warning(f"未找到要删除的反馈记录，ID {feedback_id}")
                    return False

                db.delete(feedback)
                db.commit()

                logger.info(f"已删除反馈记录，ID: {feedback_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"删除反馈记录失败，ID {feedback_id}: {e}")
            return False
