"""定时任务模块

提供热点数据的定时更新功能。
"""
import logging
import asyncio
from typing import Dict, List

from .topic_trends import TrendingTopics
from .redis_storage import RedisStorage
from .config import get_config

logger = logging.getLogger(__name__)

async def update_trending_data() -> bool:
    """更新热点数据

    1. 从API获取最新数据
    2. 处理并存储数据
    3. 清理过期数据

    Returns:
        bool: 是否更新成功
    """
    try:
        logger.info("开始更新热点数据...")

        # 初始化工具类
        config = get_config()
        logger.info(f"获取配置: {config}")

        tool = TrendingTopics()
        storage = RedisStorage(config["redis_url"])
        logger.info("工具类初始化完成")

        # 获取最新数据
        logger.info("开始获取最新数据...")
        all_topics = await tool.fetch_topics()
        if not all_topics:
            logger.error("未获取到任何数据")
            return False

        logger.info(f"获取到 {len(all_topics)} 个平台的数据")
        for platform, topics in all_topics.items():
            logger.info(f"平台 {platform}: {len(topics)} 条话题")

        # 处理并存储数据
        logger.info("开始处理和存储数据...")
        processed_data = await tool._process_topics(all_topics)
        if not processed_data:
            logger.error("数据处理失败")
            return False

        logger.info(f"处理完成，共 {len(processed_data)} 条话题")

        # 存储数据
        logger.info("开始存储数据...")
        success = await storage.store_topics(processed_data)
        if not success:
            logger.error("数据存储失败")
            return False

        logger.info("数据存储成功")

        # 清理过期数据
        logger.info("开始清理过期数据...")
        await storage.clear_expired("topic")
        logger.info("过期数据清理完成")

        logger.info("热点数据更新完成")
        return True

    except Exception as e:
        logger.error(f"更新热点数据失败: {e}")
        return False
