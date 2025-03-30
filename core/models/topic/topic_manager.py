"""主题管理器

负责管理文章主题的获取、保存等基本操作，不包含业务逻辑
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from core.models.topic.topic import Topic
from ..infra.base_manager import BaseManager
from ..infra.db_adapter import DBAdapter


class TopicManager(BaseManager[Topic]):
    """主题管理器

    提供主题相关的基本操作，包括获取、保存主题，不包含业务逻辑
    """

    _initialized: bool = False
    _model_class = Topic
    _id_field = "id"
    _timestamp_field = "updated_at"

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化主题管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        # 使用平台列表来加载话题
        # 由于没有直接的get_all_topics方法，我们使用现有方法加载
        if use_db:
            try:
                # 获取平台列表
                # 假设默认平台是general，或者可以在配置中指定
                platforms = ["general"]

                # 从各平台加载话题
                for platform in platforms:
                    topics_data = DBAdapter.get_topics_by_platform(platform)
                    for topic_data in topics_data:
                        topic = Topic(**topic_data)
                        if topic and topic.id:
                            cls._entities[topic.id] = topic

                logger.info(f"已加载 {len(cls._entities)} 个话题")
            except Exception as e:
                logger.error(f"加载话题失败: {str(e)}")

        cls._use_db = use_db
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
        # 先从内存缓存获取
        topic = cls.get_entity(topic_id)

        # 如果内存中没有，且使用数据库，则从数据库获取
        if topic is None and cls._use_db:
            try:
                topic_dict = DBAdapter.get_topic(topic_id)
                if topic_dict:
                    topic = Topic(**topic_dict)
                    if topic:
                        # 加入缓存
                        cls._entities[topic_id] = topic
            except Exception as e:
                logger.error(f"从数据库获取话题[{topic_id}]失败: {str(e)}")

        return topic

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
        # 更新时间戳
        topic.updated_at = datetime.now()

        # 使用BaseManager的save_entity方法保存到内存
        result = cls.save_entity(topic)

        # 如果使用数据库，还需保存到数据库
        if result and cls._use_db:
            try:
                topic_dict = topic.to_dict()
                db_result = DBAdapter.save_topic(topic_dict)
                if not db_result:
                    logger.warning(f"话题保存到数据库失败: {topic.id}")
                    return False
            except Exception as e:
                logger.error(f"保存话题到数据库异常: {str(e)}")
                return False

        return result

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除主题

        Args:
            topic_id: 主题ID

        Returns:
            bool: 是否成功删除
        """
        # 使用BaseManager的delete_entity方法从内存删除
        result = cls.delete_entity(topic_id)

        # 不再调用不存在的DBAdapter.delete_topic方法
        # 如果有需要在数据库层面删除话题的需求，应该使用DBAdapter中正确实现的方法
        return result

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
                content_type=content_type or "article",
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
