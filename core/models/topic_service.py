"""话题服务

提供话题相关的业务逻辑处理服务，包括获取、保存、更新话题状态等功能。
作为ContentManager与数据库之间的业务处理层。
"""

from typing import Dict, List, Optional, Any, Type, TypeVar
import json
import importlib
import time
from loguru import logger
from datetime import datetime, timedelta
from pathlib import Path
import os

from .db_adapter import DBAdapter

# 定义泛型类型变量
T = TypeVar('T')

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
                    from core.models.topic import Topic
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
                from core.models.topic import Topic
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
                from core.models.topic import Topic
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
    def sync_from_redis(cls, topics_data: List[Dict[str, Any]]) -> List[str]:
        """从Redis同步话题数据到数据库（仅用于批量迁移）

        注意：此方法主要用于批量迁移或备份目的，正常内容生产流程中
        不应该直接调用此方法，而应使用select_topic_for_production方法
        来选择并持久化单个话题。

        Args:
            topics_data: 话题数据列表

        Returns:
            List[str]: 成功同步的话题ID列表
        """
        try:
            # 使用数据库适配器同步话题
            logger.warning("执行话题批量同步操作，正常流程中不建议使用此方法")
            return DBAdapter.sync_topics_from_redis(topics_data)
        except Exception as e:
            logger.error(f"从Redis同步话题数据失败: {str(e)}")
            return []

    @classmethod
    def get_trending_topics(cls, limit: int = 100) -> List[Any]:
        """获取热门话题列表

        Args:
            limit: 返回数量限制

        Returns:
            List[Any]: 话题对象列表
        """
        try:
            # 使用数据库适配器获取热门话题
            topics_dicts = DBAdapter.get_trending_topics(limit)

            # 转换为话题对象
            try:
                from core.models.topic import Topic
                return [Topic.from_dict(topic_dict) for topic_dict in topics_dicts]
            except ImportError:
                logger.warning("话题模型导入失败，返回原始数据列表")
                return topics_dicts
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
            # 使用数据库适配器获取最新话题
            topics_dicts = DBAdapter.get_latest_topics(limit)

            # 转换为话题对象
            try:
                from core.models.topic import Topic
                return [Topic.from_dict(topic_dict) for topic_dict in topics_dicts]
            except ImportError:
                logger.warning("话题模型导入失败，返回原始数据列表")
                return topics_dicts
        except Exception as e:
            logger.error(f"获取最新话题失败: {str(e)}")
            return []

    @classmethod
    def select_topic_for_production(cls, platform: str, content_type: str = None) -> Optional[Any]:
        """选择一个待处理状态的话题用于内容生产并更新其状态

        从数据库中获取状态为pending的话题，按照综合评分选择最适合的一个，
        并将其状态更新为selected

        注意：该方法假设话题已经被保存到数据库中，controller层应该
        确保在调用此方法前，已经将所需的话题保存到了数据库。

        Args:
            platform: 平台标识
            content_type: 内容类型ID，可选

        Returns:
            Optional[Any]: 选择的话题对象，如无合适话题则返回None
        """
        try:
            # 获取待处理的话题
            topics_dicts = DBAdapter.get_topics_by_status("pending")

            # 按平台过滤
            if platform:
                topics_dicts = [t for t in topics_dicts if t.get('platform') == platform]

            # 按内容类型过滤
            if content_type:
                topics_dicts = [t for t in topics_dicts if not t.get('content_type') or
                              t.get('content_type') == content_type]

            if not topics_dicts:
                logger.warning(f"数据库中未找到符合条件的待处理话题: 平台={platform}, 内容类型={content_type}")
                return None

            # 根据时间和热度排序（简单的加权评分）
            now = int(time.time())

            def score_topic(topic):
                age = now - topic.get('fetch_time', now)
                age_factor = max(0, 1 - (age / (7 * 24 * 3600)))  # 7天内的时效性
                hot_score = topic.get('hot', 0) / 100 if topic.get('hot', 0) > 0 else 0
                trend_score = topic.get('trend_score', 0) if topic.get('trend_score', 0) > 0 else 0
                return (age_factor * 0.4) + (hot_score * 0.3) + (trend_score * 0.3)

            # 按综合得分排序
            topics_dicts.sort(key=score_topic, reverse=True)

            # 选择得分最高的话题
            selected_topic_dict = topics_dicts[0]

            # 更新状态为selected
            if DBAdapter.update_topic_status(selected_topic_dict['id'], "selected"):
                logger.info(f"已选择话题[{selected_topic_dict['id']}:{selected_topic_dict.get('title', '')}]用于内容生产")

                # 转换为话题对象
                try:
                    from core.models.topic import Topic
                    return Topic.from_dict(selected_topic_dict)
                except ImportError:
                    logger.warning("话题模型导入失败，返回原始数据字典")
                    return selected_topic_dict
            else:
                logger.error(f"更新话题[{selected_topic_dict['id']}]状态失败")
                return None
        except Exception as e:
            logger.error(f"选择话题失败: {str(e)}")
            return None
