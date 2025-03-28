"""话题服务

提供话题相关的业务逻辑处理服务，包括获取、保存、更新话题状态等功能。
作为ContentManager与数据库之间的业务处理层。
"""

from typing import Dict, List, Optional, Any, Type, TypeVar, Union, Tuple
import json
import importlib
import time
import logging
from loguru import logger
from datetime import datetime, timedelta
from pathlib import Path
import os

from .db_adapter import DBAdapter
try:
    from .redis_tool import RedisTool
except ImportError:
    class RedisTool:
        @staticmethod
        def get_all_topics():
            return []

        @staticmethod
        def clear_topics():
            pass

try:
    from core.models.topic import Topic
except ImportError:
    # 处理导入失败情况，定义一个占位Topic类
    class Topic:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

# 定义泛型类型变量
T = Any

# 日志配置
logger = logging.getLogger(__name__)

class TopicService:
    """话题服务类

    提供话题相关的业务逻辑服务，负责话题的获取、保存、状态管理等功能。
    该类是纯业务逻辑层，不包含数据访问逻辑，所有数据操作都通过DBAdapter完成。
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
                    return Topic.from_dict(topic_dict)
                except ImportError:
                    logger.warning("话题模型导入失败，返回原始数据字典")
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
            # 使用数据库适配器保存话题
            return DBAdapter.save_topic(topic)
        except Exception as e:
            logger.error(f"保存话题失败: {str(e)}")
            return False

    @classmethod
    def update_topic_status(cls, topic_id: str, status: str) -> bool:
        """更新话题状态

        Args:
            topic_id: 话题ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        try:
            # 使用数据库适配器更新话题状态
            return DBAdapter.update_topic_status(topic_id, status)
        except Exception as e:
            logger.error(f"更新话题[{topic_id}]状态失败: {str(e)}")
            return False

    @classmethod
    def get_topics_by_platform(cls, platform: str) -> List[Any]:
        """获取指定平台的所有话题

        Args:
            platform: 平台标识

        Returns:
            List[Any]: 话题对象列表
        """
        try:
            # 使用数据库适配器获取话题列表
            topics_dicts = DBAdapter.get_topics_by_platform(platform)

            # 转换为话题对象
            try:
                return [Topic.from_dict(topic_dict) for topic_dict in topics_dicts]
            except ImportError:
                logger.warning("话题模型导入失败，返回原始数据列表")
                return topics_dicts
        except Exception as e:
            logger.error(f"获取平台[{platform}]话题失败: {str(e)}")
            return []

    @classmethod
    def get_topics_by_status(cls, status: str) -> List[Any]:
        """获取指定状态的所有话题

        Args:
            status: 话题状态

        Returns:
            List[Any]: 话题对象列表
        """
        try:
            # 使用数据库适配器获取话题列表
            topics_dicts = DBAdapter.get_topics_by_status(status)

            # 转换为话题对象
            try:
                return [Topic.from_dict(topic_dict) for topic_dict in topics_dicts]
            except ImportError:
                logger.warning("话题模型导入失败，返回原始数据列表")
                return topics_dicts
        except Exception as e:
            logger.error(f"获取状态[{status}]话题失败: {str(e)}")
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
            # 使用数据库适配器删除话题
            return DBAdapter.delete_topic(topic_id)
        except Exception as e:
            logger.error(f"删除话题[{topic_id}]失败: {str(e)}")
            return False

    @classmethod
    def get_trending_topics(cls, platform: Optional[str] = None, limit: int = 10) -> List[Any]:
        """获取热门话题

        Args:
            platform: 平台名称
            limit: 返回数量限制

        Returns:
            List[Any]: 话题对象列表
        """
        try:
            # 初始化数据库
            if not DBAdapter.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取最新话题
            topics = topic_repo.get_latest(limit=limit)
            if not topics:
                return []

            # 过滤平台
            if platform:
                topics = [t for t in topics if t.platform == platform]

            # 转换为Topic模型
            result = []
            for t in topics:
                # 转换为字典
                topic_dict = t.to_dict()

                # 创建Topic对象
                topic = Topic(
                    id=topic_dict.get('id'),
                    title=topic_dict.get('title'),
                    platform=topic_dict.get('platform', ''),
                    description=topic_dict.get('description', ''),
                    url=topic_dict.get('url', ''),
                    mobile_url=topic_dict.get('mobile_url', ''),
                    cover=topic_dict.get('cover', ''),
                    hot=topic_dict.get('hot', 0),
                    trend_score=topic_dict.get('trend_score', 0),
                    source_time=topic_dict.get('source_time', 0),
                    expire_time=topic_dict.get('expire_time', 0)
                )
                result.append(topic)

            return result
        except Exception as e:
            logger.error(f"获取热门话题失败: {str(e)}")
            return []

    @classmethod
    def get_latest_topics(cls, limit: int = 100) -> List[Any]:
        """获取最新的话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Any]: 话题对象列表
        """
        try:
            # 初始化数据库
            if not DBAdapter.initialize():
                return []

            # 导入仓库
            from core.db.repository import topic_repo

            # 获取最新话题
            topics = topic_repo.get_latest(limit=limit)
            if not topics:
                return []

            # 转换为Topic模型
            result = []
            for t in topics:
                # 转换为字典
                topic_dict = t.to_dict()

                # 创建Topic对象
                topic = Topic(
                    id=topic_dict.get('id'),
                    title=topic_dict.get('title'),
                    platform=topic_dict.get('platform', ''),
                    description=topic_dict.get('description', ''),
                    url=topic_dict.get('url', ''),
                    mobile_url=topic_dict.get('mobile_url', ''),
                    cover=topic_dict.get('cover', ''),
                    hot=topic_dict.get('hot', 0),
                    trend_score=topic_dict.get('trend_score', 0),
                    source_time=topic_dict.get('source_time', 0),
                    expire_time=topic_dict.get('expire_time', 0)
                )
                result.append(topic)

            return result
        except Exception as e:
            logger.error(f"获取最新话题失败: {str(e)}")
            return []

    @classmethod
    def process_data(cls) -> bool:
        """处理话题数据

        从Redis获取话题数据，保存到数据库

        Returns:
            bool: 是否处理成功
        """
        try:
            # 获取话题数据
            topics = RedisTool.get_all_topics()
            if not topics:
                logger.info("没有发现话题数据")
                return True

            # 初始化数据库
            if not DBAdapter.initialize():
                logger.error("数据库初始化失败")
                return False

            # 导入仓库
            from core.db.repository import topic_repo

            # 保存话题数据
            for item in topics:
                # 验证必须的字段
                if 'id' not in item or 'title' not in item:
                    logger.warning(f"话题数据缺少必要字段: {item}")
                    continue

                # 检查是否已存在
                existing = topic_repo.get(item['id'])
                if existing:
                    # 更新话题
                    topic_repo.update(item['id'], item)
                    logger.info(f"更新话题: {item['id']}")
                else:
                    # 创建话题
                    topic_repo.create(item)
                    logger.info(f"创建话题: {item['id']}")

            # 清理Redis数据
            RedisTool.clear_topics()
            return True
        except Exception as e:
            logger.error(f"处理话题数据失败: {str(e)}")
            return False
