"""热点数据处理模块

负责对原始热点数据进行标准化处理。
将不同平台的数据格式统一化，便于后续处理。
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TopicProcessor:
    """话题数据标准化处理器

    功能:
    1. 数据格式统一化
    2. 字段标准化处理
    3. 热度值标准化
    4. 时间格式标准化
    """

    # 热度值单位转换
    HOT_UNITS = {
        "万": 10000,
        "w": 10000,
        "W": 10000,
        "k": 1000,
        "K": 1000,
        "亿": 100000000,
    }

    def __init__(self):
        """初始化处理器"""
        logger.info("初始化话题处理器")

    def process_platform_data(self, platform: str, raw_data: Dict) -> List[Dict]:
        """处理单个平台的原始数据

        Args:
            platform: 平台名称
            raw_data: 原始数据

        Returns:
            List[Dict]: 标准化后的话题列表
        """
        try:
            # 获取原始话题列表
            topics = raw_data.get("data", [])
            if not isinstance(topics, list):
                logger.error(f"平台 {platform} 数据格式错误: data 字段不是列表")
                return []

            # 处理每个话题
            processed_topics = []
            for topic in topics:
                try:
                    processed_topic = self._standardize_topic(platform, topic)
                    if processed_topic:
                        processed_topics.append(processed_topic)
                except Exception as e:
                    logger.error(f"话题处理失败: {e}, 平台: {platform}, 原始数据: {topic}")
                    continue

            logger.info(f"平台 {platform} 处理完成: {len(processed_topics)}/{len(topics)} 个话题")
            return processed_topics

        except Exception as e:
            logger.error(f"平台 {platform} 数据处理失败: {e}")
            return []

    def _standardize_topic(self, platform: str, raw_topic: Dict) -> Optional[Dict]:
        """标准化单个话题数据

        Args:
            platform: 平台名称
            raw_topic: 原始话题数据

        Returns:
            Optional[Dict]: 标准化后的话题数据，无效数据返回None
        """
        # 必需字段检查
        title = str(raw_topic.get("title", "")).strip()
        if not title:
            logger.warning(f"话题缺少标题: {raw_topic}")
            return None

        # 构建基础数据结构
        topic = {
            "title": title,
            "platform": platform,
            "raw_data": raw_topic,  # 保留原始数据
            "update_time": self._standardize_time(raw_topic.get("timestamp")),
        }

        # 处理URL
        if "url" in raw_topic:
            topic["url"] = str(raw_topic["url"])
        if "mobileUrl" in raw_topic:
            topic["mobile_url"] = str(raw_topic["mobileUrl"])

        # 处理热度值
        if "hot" in raw_topic:
            topic["hot_score"] = self._standardize_hot_value(raw_topic["hot"])
            topic["raw_hot"] = raw_topic["hot"]  # 保留原始热度值

        # 处理可选字段
        if "desc" in raw_topic:
            topic["description"] = str(raw_topic["desc"])
        if "cover" in raw_topic:
            topic["cover"] = str(raw_topic["cover"])
        if "author" in raw_topic:
            topic["author"] = str(raw_topic["author"])

        return topic

    def _standardize_hot_value(self, hot_value) -> int:
        """标准化热度值

        Args:
            hot_value: 原始热度值

        Returns:
            int: 标准化后的热度值
        """
        try:
            if isinstance(hot_value, (int, float)):
                return int(hot_value)

            if isinstance(hot_value, str):
                # 移除多余字符
                hot_str = hot_value.strip().replace("+", "").replace("热度", "")

                # 处理带单位的数值
                for unit, multiplier in self.HOT_UNITS.items():
                    if unit in hot_str:
                        number = float(hot_str.replace(unit, ""))
                        return int(number * multiplier)

                # 处理纯数字
                return int(float(hot_str))

            logger.warning(f"无法处理的热度值类型: {type(hot_value)}")
            return 0

        except (TypeError, ValueError) as e:
            logger.warning(f"热度值处理失败: {e}, 原始值: {hot_value}")
            return 0

    def _standardize_time(self, timestamp) -> str:
        """标准化时间格式

        Args:
            timestamp: 原始时间戳或时间字符串

        Returns:
            str: ISO格式的时间字符串
        """
        try:
            if isinstance(timestamp, (int, float)):
                # 处理时间戳
                dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                # 尝试解析常见的时间格式
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    # 如果解析失败，使用当前时间
                    dt = datetime.now()
            else:
                dt = datetime.now()

            return dt.isoformat()

        except Exception as e:
            logger.warning(f"时间格式化失败: {e}, 使用当前时间")
            return datetime.now().isoformat()
