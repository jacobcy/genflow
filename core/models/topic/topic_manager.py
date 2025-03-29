"""主题管理器

负责管理文章主题的获取、保存等基本操作，不包含业务逻辑
"""

from typing import Dict, List, Optional, Any, ClassVar
from datetime import datetime
from loguru import logger

from core.models.topic.topic import Topic
from ..infra.base_manager import BaseManager
from ..infra.db_adapter import DBAdapter


class TopicManager(BaseManager):
    """主题管理器

    提供主题相关的基本操作，包括获取、保存主题，不包含业务逻辑
    """

    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化主题管理器"""
        if cls._initialized:
            return

        cls._initialized = True
        logger.info("主题管理器初始化完成")

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Topic]:
        """获取指定ID的主题

        Args:
            topic_id: 主题ID

        Returns:
            Optional[Topic]: 主题对象，不存在则返回None
        """
        cls.ensure_initialized()

        try:
            # 从数据库获取话题数据
            topic_dict = DBAdapter.get_topic(topic_id)
            if not topic_dict:
                logger.warning(f"话题不存在: {topic_id}")
                return None

            # 创建话题对象
            return Topic(**topic_dict)
        except Exception as e:
            logger.error(f"获取话题失败: {str(e)}")
            return None

    @classmethod
    def get_topic_by_id(cls, topic_id: str) -> Optional[Topic]:
        """获取指定ID的主题（别名方法）

        Args:
            topic_id: 主题ID

        Returns:
            Optional[Topic]: 主题对象，不存在则返回None
        """
        return cls.get_topic(topic_id)

    @classmethod
    def save_topic(cls, topic: Topic) -> bool:
        """保存主题

        Args:
            topic: 主题对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        try:
            # 更新时间戳
            topic.updated_at = datetime.now()

            # 保存到数据库
            result = DBAdapter.save_topic(topic.to_dict())
            if result:
                logger.info(f"话题保存成功: {topic.id} ({topic.title})")
            else:
                logger.warning(f"话题保存失败: {topic.id}")
            return result
        except Exception as e:
            logger.error(f"保存话题异常: {str(e)}")
            return False

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除主题

        Args:
            topic_id: 主题ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()

        try:
            # 从数据库删除话题
            result = DBAdapter.delete_topic(topic_id)
            if result:
                logger.info(f"话题删除成功: {topic_id}")
            else:
                logger.warning(f"话题删除失败，可能不存在: {topic_id}")
            return result
        except Exception as e:
            logger.error(f"删除话题异常: {str(e)}")
            return False

    @classmethod
    def create_topic(cls, title: str, keywords: Optional[List[str]] = None,
                   content_type: Optional[str] = None) -> Optional[Topic]:
        """创建新主题

        Args:
            title: 主题标题
            keywords: 主题关键词列表
            content_type: 内容类型ID

        Returns:
            Optional[Topic]: 创建的主题对象，失败返回None
        """
        if not keywords:
            keywords = []

        try:
            # 创建话题对象
            now = datetime.now()
            topic = Topic(
                title=title,
                keywords=keywords,
                content_type=content_type,
                created_at=now,
                updated_at=now
            )

            # 保存话题
            if cls.save_topic(topic):
                return topic
            return None
        except Exception as e:
            logger.error(f"创建话题异常: {str(e)}")
            return None
