"""主题管理器

负责管理话题的获取、保存等基本操作，不包含业务逻辑。
专注于外部抓取话题的持久化管理。
"""

from typing import List, Optional
from loguru import logger

from core.models.topic.topic import Topic # Pydantic model
from ..infra.base_manager import BaseManager
from core.models.db.session import get_db # Function to get DB session context
from .topic_db import Topic as TopicDB # SQLAlchemy model


class TopicManager(BaseManager):
    """主题管理器 (Refactored)

    提供主题相关的基本 CRUD 操作，直接与数据库交互。
    继承自 BaseManager，负责 TopicDB 模型的持久化。
    """

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化主题管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        super().initialize(use_db)
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
        if not cls._use_db:
            logger.warning("数据库未启用，无法获取主题。")
            # Add logic here to retrieve from memory/file if not using DB
            return None

        try:
            with get_db() as db: # Use session context manager
                topic_db = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
                if not topic_db:
                    logger.warning(f"数据库中未找到话题: {topic_id}")
                    return None

                # Convert SQLAlchemy model to Pydantic model
                # 需要先转换为字典，然后创建Pydantic模型
                topic_dict = {
                    'id': topic_db.id,
                    'title': topic_db.title,
                    'description': getattr(topic_db, 'description', ''),
                    'platform': getattr(topic_db, 'platform', ''),
                    'url': getattr(topic_db, 'url', ''),
                    'mobile_url': getattr(topic_db, 'mobile_url', ''),
                    'hot': getattr(topic_db, 'hot', 0),
                    'cover': getattr(topic_db, 'cover', ''),
                    'created_at': getattr(topic_db, 'created_at', None),
                    'updated_at': getattr(topic_db, 'updated_at', None),
                    'source_time': getattr(topic_db, 'source_time', None),
                    'expire_time': getattr(topic_db, 'expire_time', None),
                }
                return Topic(**topic_dict)
        except Exception as e:
            logger.error(f"从数据库获取话题[{topic_id}]失败: {str(e)}")
            return None

    @classmethod
    def save_topic(cls, topic: Topic) -> bool:
        """保存主题 (创建或更新)

        Args:
            topic: 主题对象 (Pydantic model)

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法保存主题。")
            # Add logic here to save to memory/file if not using DB
            return False

        try:
            with get_db() as db: # Use session context manager
                # Check if topic exists
                topic_db = db.query(TopicDB).filter(TopicDB.id == topic.id).first()

                if topic_db:
                    # Update existing topic
                    logger.debug(f"Updating existing topic {topic.id} in DB.")
                    # Update fields from Pydantic model to SQLAlchemy model
                    for key, value in topic.model_dump().items():
                        if hasattr(topic_db, key):
                            setattr(topic_db, key, value)
                    # topic_db.updated_at = datetime.utcnow() # Handled by Pydantic model? or DB?
                else:
                    # Create new topic
                    logger.debug(f"Creating new topic {topic.id} in DB.")
                    # Convert Pydantic model to SQLAlchemy model instance
                    topic_data = topic.model_dump()
                    topic_db = TopicDB(**topic_data)
                    db.add(topic_db)

                db.commit()
                # db.refresh(topic_db) # Optional: refresh if needed
                logger.info(f"话题 {topic.id} 成功保存到数据库。")
                return True
        except Exception as e:
            logger.error(f"保存话题[{topic.id}]到数据库失败: {str(e)}")
            # 不需要手动回滚，with get_db() 上下文会处理
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
        if not cls._use_db:
            logger.warning("数据库未启用，无法删除主题。")
            # Add logic here to delete from memory/file if not using DB
            return False

        try:
            with get_db() as db: # Use session context manager
                topic_db = db.query(TopicDB).filter(TopicDB.id == topic_id).first()
                if topic_db:
                    db.delete(topic_db)
                    db.commit()
                    logger.info(f"话题 {topic_id} 已从数据库删除。")
                    return True
                else:
                    logger.warning(f"尝试删除的话题不存在: {topic_id}")
                    return False # Or True, depending on desired idempotency behavior
        except Exception as e:
            logger.error(f"从数据库删除话题[{topic_id}]失败: {str(e)}")
            # 不需要手动回滚，with get_db() 上下文会处理
            return False

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Topic]:
        """获取指定平台的所有话题

        Args:
            platform: 平台名称

        Returns:
            List[Topic]: 话题列表
        """
        cls.ensure_initialized()
        if not cls._use_db:
            logger.warning("数据库未启用，无法按平台获取话题。")
            # Add logic here to retrieve from memory/file if not using DB
            return []

        topics = []
        try:
            with get_db() as db: # Use session context manager
                topics_db = db.query(TopicDB).filter(TopicDB.platform == platform).all() # Assuming 'platform' field exists
                if not topics_db:
                    logger.debug(f"数据库中未找到平台 {platform} 的话题。")
                    return []

                # Convert SQLAlchemy models to Pydantic models
                for topic_db in topics_db:
                    try:
                        # 需要先转换为字典，然后创建Pydantic模型
                        topic_dict = {
                            'id': topic_db.id,
                            'title': topic_db.title,
                            'description': getattr(topic_db, 'description', ''),
                            'platform': getattr(topic_db, 'platform', ''),
                            'url': getattr(topic_db, 'url', ''),
                            'mobile_url': getattr(topic_db, 'mobile_url', ''),
                            'hot': getattr(topic_db, 'hot', 0),
                            'cover': getattr(topic_db, 'cover', ''),
                            'created_at': getattr(topic_db, 'created_at', None),
                            'updated_at': getattr(topic_db, 'updated_at', None),
                            'source_time': getattr(topic_db, 'source_time', None),
                            'expire_time': getattr(topic_db, 'expire_time', None),
                        }
                        topics.append(Topic(**topic_dict))
                    except Exception as validation_error:
                         logger.warning(f"转换话题DB对象失败 (ID: {getattr(topic_db, 'id', 'N/A')}): {validation_error}")
            return topics
        except Exception as e:
            logger.error(f"从数据库获取平台[{platform}]话题失败: {str(e)}")
            return []

    @classmethod
    def create_topic(cls, title: str, keywords: Optional[List[str]] = None,
                  content_type: Optional[str] = None) -> Optional[Topic]:
        """
        创建新话题

        注意：此方法仅为兼容 ContentManager 接口，实际上话题应从外部抓取而非内部创建。
        在实际使用中，应优先考虑直接使用 save_topic 方法保存从外部获取的话题。

        Args:
            title: 话题标题
            keywords: 话题关键词列表（已废弃，仅为兼容保留）
            content_type: 内容类型ID（已废弃，仅为兼容保留）

        Returns:
            Optional[Topic]: 创建的话题对象，失败返回None
        """
        cls.ensure_initialized()
        logger.warning("创建话题方法已废弃，话题应从外部抓取而非内部创建")

        try:
            # 创建基本话题
            topic = Topic(
                title=title,
                description="",
                platform=""
            )

            # 保存话题
            if cls.save_topic(topic):
                return topic
            return None
        except Exception as e:
            logger.error(f"创建话题失败: {str(e)}")
            return None
