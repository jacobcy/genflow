"""话题适配器

负责话题数据的数据库访问操作。
"""

from typing import Dict, List, Optional, Any
import time
from loguru import logger


class TopicAdapter:
    """话题适配器，负责处理话题相关的数据库操作"""

    _is_initialized: bool = False

    @classmethod
    def initialize(cls) -> bool:
        """初始化数据库连接

        Returns:
            bool: 是否成功初始化
        """
        if cls._is_initialized:
            return True

        try:
            # 导入数据库初始化模块
            from core.models.db.initialize import initialize_all

            # 初始化数据库
            initialize_all()

            cls._is_initialized = True
            logger.info("话题适配器初始化成功")
            return True
        except ImportError as e:
            logger.warning(f"数据库模块导入失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            return False

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Dict[str, Any]]:
        """从数据库获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Dict[str, Any]]: 话题数据，如不存在返回None
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.models.db.repository import topic_repo

            # 获取话题
            topic = topic_repo.get(topic_id)
            if topic and hasattr(topic, 'to_dict'):
                return topic.to_dict()
            elif topic:
                return dict(topic)
            return None
        except Exception as e:
            logger.error(f"获取话题[{topic_id}]失败: {str(e)}")
            return None

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题到数据库

        Args:
            topic: 话题对象

        Returns:
            bool: 是否成功保存
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.models.db.repository import topic_repo

            # 转换为字典
            topic_dict = cls._get_topic_dict(topic)

            # 确保必须的字段
            if 'id' not in topic_dict or 'title' not in topic_dict or 'platform' not in topic_dict:
                logger.error("保存话题失败: 缺少必要字段(id, title, platform)")
                return False

            # 检查是否已存在
            existing = topic_repo.get(topic_dict['id'])
            if existing:
                # 更新
                updated = topic_repo.update(topic_dict['id'], topic_dict)
                if updated:
                    logger.info(f"成功更新话题: {topic_dict['id']}")
                    return True
                else:
                    logger.error(f"更新话题失败: {topic_dict['id']}")
                    return False
            else:
                # 创建
                created = topic_repo.create(topic_dict)
                if created:
                    logger.info(f"成功创建话题: {topic_dict['id']}")
                    return True
                else:
                    logger.error(f"创建话题失败")
                    return False
        except Exception as e:
            logger.error(f"保存话题失败: {str(e)}")
            return False

    @staticmethod
    def _get_topic_dict(topic: Any) -> Dict[str, Any]:
        """将话题对象转换为字典

        Args:
            topic: 话题对象

        Returns:
            Dict[str, Any]: 话题字典
        """
        if hasattr(topic, "to_dict"):
            return topic.to_dict()

        # 直接使用对象属性构建字典
        topic_dict = {}
        for key in ['id', 'title', 'platform', 'description', 'url', 'mobile_url',
                  'cover', 'hot', 'trend_score', 'source_time', 'expire_time']:
            if hasattr(topic, key):
                topic_dict[key] = getattr(topic, key)

        # 确保时间戳字段
        if 'source_time' not in topic_dict:
            topic_dict['source_time'] = int(time.time())
        if 'expire_time' not in topic_dict:
            # 默认7天后过期
            topic_dict['expire_time'] = int(time.time()) + 7 * 24 * 60 * 60

        return topic_dict

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Dict[str, Any]]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Dict[str, Any]]: 话题列表
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return []

            # 导入仓库
            from core.models.db.repository import topic_repo

            # 获取话题
            topics = topic_repo.get_by_platform(platform)

            # 转换为字典列表
            return [
                topic.to_dict() if hasattr(topic, 'to_dict') else dict(topic)
                for topic in topics
            ]
        except Exception as e:
            logger.error(f"获取平台话题失败: {str(e)}")
            return []

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.models.db.repository import topic_repo

            # 删除话题
            success = topic_repo.delete(topic_id)

            if success:
                logger.info(f"成功删除话题: {topic_id}")
            else:
                logger.warning(f"删除话题失败, 未找到话题: {topic_id}")

            return success
        except Exception as e:
            logger.error(f"删除话题失败: {str(e)}")
            return False
