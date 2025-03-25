"""工具类

提供话题处理、数据转换和评分计算等功能。
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .platform_weights import (
    calculate_normalized_hot_score,
    get_platform_weight,
    get_default_hot_score,
    PLATFORM_WEIGHTS,
    DEFAULT_HOT_SCORES
)
from .platform_categories import (
    PLATFORM_CATEGORIES,
    get_platforms_by_category,
    get_platform_categories,
    CATEGORY_TAGS
)

logger = logging.getLogger(__name__)

def parse_hot_value(hot_value: any) -> Optional[int]:
    """解析热度值

    Args:
        hot_value: 原始热度值，可能是字符串或数字

    Returns:
        Optional[int]: 解析后的整数热度值，解析失败返回None
    """
    if hot_value is None:
        return None

    if isinstance(hot_value, (int, float)):
        return int(hot_value)

    if isinstance(hot_value, str):
        # 移除逗号和其他非数字字符
        clean_str = ''.join(c for c in hot_value if c.isdigit())
        try:
            return int(clean_str) if clean_str else None
        except ValueError:
            return None

    return None

class TokenCounter:
    """字符计数器（简化版token计数）"""

    @staticmethod
    def count_topic_tokens(topic: Dict) -> int:
        """计算单个话题的字符数

        Args:
            topic: 话题数据字典

        Returns:
            int: 字符总数
        """
        total = 0
        # 计算标题字符数
        total += len(topic.get("title", ""))
        # 计算描述字符数
        total += len(topic.get("description", ""))
        # 计算平台名称字符数
        total += len(topic.get("platform", ""))
        return total

    @staticmethod
    def estimate_total_tokens(topics: List[Dict]) -> int:
        """估算话题列表的总字符数

        Args:
            topics: 话题列表

        Returns:
            int: 估算的总字符数
        """
        return sum(TokenCounter.count_topic_tokens(topic) for topic in topics)

class TopicProcessor:
    """话题数据处理器"""

    def process_topics(self, topics: List[Dict], platform: str) -> List[Dict]:
        """处理话题数据

        Args:
            topics: 原始话题列表
            platform: 平台名称

        Returns:
            List[Dict]: 处理后的话题列表
        """
        processed = []
        current_time = datetime.now()
        crawl_time = int(current_time.timestamp())
        expire_time = int((current_time + timedelta(days=7)).timestamp())

        for topic in topics:
            if not isinstance(topic, dict):
                logger.warning(f"跳过非字典类型数据: {topic}")
                continue

            # 如果没有标题，直接跳过
            title = topic.get("title")
            if not title:
                logger.debug(f"跳过无标题话题: {topic}")
                continue

            try:
                # 处理热度值
                hot_value = parse_hot_value(topic.get("hot"))
                hot_score = calculate_normalized_hot_score(platform, hot_value)

                # 处理时间戳
                timestamp = topic.get("timestamp")
                try:
                    if timestamp is not None:
                        if isinstance(timestamp, (int, float)):
                            timestamp = int(timestamp)
                        elif isinstance(timestamp, str):
                            timestamp = int(float(timestamp))
                        else:
                            timestamp = crawl_time
                    else:
                        timestamp = crawl_time
                except (TypeError, ValueError):
                    timestamp = crawl_time
                    logger.debug(f"时间戳解析失败，使用抓取时间: {crawl_time}")

                # 创建基础话题数据
                processed_topic = {
                    "title": str(title).strip(),
                    "platform": platform,
                    "timestamp": timestamp,
                    "hot_score": hot_score,
                    "fetch_time": crawl_time,
                    "expire_time": expire_time
                }

                # 直接保留原始字段值，不做类型转换
                for field in ["url", "description", "desc", "mobile_url", "mobileUrl", "cover"]:
                    if field in topic and topic[field]:  # 只保留非空值
                        # 将desc和mobileUrl标准化为description和mobile_url
                        if field == "desc":
                            processed_topic["description"] = str(topic[field]).strip()
                        elif field == "mobileUrl":
                            processed_topic["mobile_url"] = str(topic[field]).strip()
                        else:
                            processed_topic[field] = str(topic[field]).strip()

                processed.append(processed_topic)

            except Exception as e:
                logger.warning(f"话题处理失败: {e}, 原始数据: {topic}")
                continue

        return processed

    def calculate_priority_score(self, topic: Dict) -> int:
        """计算话题优先级分数

        Args:
            topic: 话题数据

        Returns:
            int: 优先级分数
        """
        platform = topic.get("platform", "")
        hot_score = topic.get("hot_score")

        # 如果hot_score为None，使用平台默认值
        if hot_score is None:
            hot_score = get_default_hot_score(platform)
            logger.debug(f"使用平台 {platform} 默认热度值: {hot_score}")

        # 获取时间戳，优先使用原始时间戳，否则使用抓取时间
        timestamp = topic.get("timestamp") or topic.get("fetch_time", 0)
        current_time = datetime.now().timestamp()
        time_factor = max(0, 1 - (current_time - timestamp) / (7 * 24 * 3600))  # 7天时效性衰减

        # 获取平台权重作为基础分数权重
        platform_weight = get_platform_weight(platform)

        # 热度占70%，时效性占20%，平台权重占10%
        return int(hot_score * (0.7 + 0.2 * time_factor + 0.1 * platform_weight))

class TopicFilter:
    """话题过滤器"""

    def filter_by_category(self, topics: List[Dict], category: str) -> List[Dict]:
        """按分类过滤话题

        Args:
            topics: 话题列表
            category: 目标分类

        Returns:
            List[Dict]: 过滤后的话题列表
        """
        if not category or category not in CATEGORY_TAGS:
            return topics

        filtered = []
        target_platforms = get_platforms_by_category(category)

        for topic in topics:
            platform = topic.get("platform")
            if platform in target_platforms:
                filtered.append(topic)

        return filtered

    def search_topics(self, topics: List[Dict], keywords: str) -> List[Dict]:
        """搜索话题

        Args:
            topics: 话题列表
            keywords: 搜索关键词

        Returns:
            List[Dict]: 匹配的话题列表
        """
        if not keywords:
            return topics

        matched = []
        for topic in topics:
            title = topic.get("title", "").lower()
            desc = topic.get("description", "").lower()
            keywords = keywords.lower()

            # 简单的关键词匹配
            if keywords in title or keywords in desc:
                matched.append(topic)

        return matched
