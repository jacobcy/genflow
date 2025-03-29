"""话题服务

提供话题相关的基本数据服务，作为ContentManager与数据库之间的适配层，
不包含复杂业务逻辑或话题生成逻辑。
"""

from typing import Dict, List, Optional, Any, Union
import time
import logging
from loguru import logger

from ..infra.db_adapter import DBAdapter

try:
    from core.models.topic.topic import Topic
except ImportError:
    # 处理导入失败情况，定义一个占位Topic类
    class Topic:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# 日志配置
logger = logging.getLogger(__name__)

class TopicService:
    """话题服务类

    提供话题相关的基本数据服务，负责话题的获取、保存等功能。
    该类是纯适配层，不包含业务逻辑，所有数据操作都通过DBAdapter完成。
    """

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Any]:
        """获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Any]: 话题对象，如不存在返回None
        """
        try:
            # 使用数据库适配器获取话题
            topic_dict = DBAdapter.get_topic(topic_id)

            if topic_dict:
                # 导入话题模型
                try:
                    return Topic(**topic_dict)
                except Exception:
                    logger.warning("话题模型转换失败，返回原始数据字典")
                    return topic_dict

            logger.warning(f"话题[{topic_id}]不存在")
            return None
        except Exception as e:
            logger.error(f"获取话题[{topic_id}]失败: {str(e)}")
            return None

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题

        Args:
            topic: 话题对象或字典

        Returns:
            bool: 是否成功保存
        """
        try:
            # 转换为字典
            topic_dict = topic
            if hasattr(topic, 'to_dict'):
                topic_dict = topic.to_dict()

            # 使用数据库适配器保存话题
            result = DBAdapter.save_topic(topic_dict)
            if result:
                logger.info(f"话题保存成功: {topic_dict.get('id')}")
            else:
                logger.warning(f"话题保存失败: {topic_dict.get('id')}")
            return result
        except Exception as e:
            logger.error(f"保存话题失败: {str(e)}")
            return False

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 使用数据库适配器删除话题
            result = DBAdapter.delete_topic(topic_id)
            if result:
                logger.info(f"话题删除成功: {topic_id}")
            else:
                logger.warning(f"话题删除失败: {topic_id}")
            return result
        except Exception as e:
            logger.error(f"删除话题[{topic_id}]失败: {str(e)}")
            return False

    @classmethod
    def create_topic(cls, title: str, **kwargs) -> Optional[Any]:
        """创建话题

        Args:
            title: 话题标题
            **kwargs: 其他话题属性

        Returns:
            Optional[Any]: 创建的话题对象，如失败返回None
        """
        try:
            # 创建话题对象
            now = int(time.time())
            topic_data = {
                'title': title,
                'created_at': now,
                'updated_at': now,
                **kwargs
            }

            # 创建话题对象
            try:
                topic = Topic(**topic_data)
                if hasattr(topic, 'to_dict'):
                    topic_data = topic.to_dict()
            except Exception:
                logger.warning("话题模型创建失败，使用原始数据")

            # 保存到数据库
            if cls.save_topic(topic_data):
                # 返回创建的话题
                return cls.get_topic(topic_data.get('id'))
            return None
        except Exception as e:
            logger.error(f"创建话题失败: {str(e)}")
            return None
