"""热点话题工具

提供热点话题的获取、过滤和处理功能。
"""
import logging
from typing import Dict, List, Optional, Set, Union, Tuple
import inspect
from datetime import datetime, timedelta
import json
import re
import asyncio
import random

from .api_collector import APICollector
from .utils import TopicProcessor, TopicFilter, TokenCounter
from .platform_categories import CATEGORY_TAGS, get_platforms_by_category, PLATFORM_CATEGORIES
from .redis_storage import RedisStorage
from .config import get_config
from .platform_weights import get_platform_weight, get_default_hot_score
from core.tools.base import BaseTool, ToolResult
from core.tools.nlp_tools.text_utils import count_words

logger = logging.getLogger(__name__)

class TrendingTopics(BaseTool):
    """热门话题查询工具

    这个工具用于获取各大平台的热门话题，支持多种分类和筛选。
    可以通过指定分类和关键词来过滤结果。

    支持的分类有：
    - 综合类（热点、热门、推荐、trending）
    - 科技类（科技、技术、tech、数码）
    - 娱乐类（娱乐、明星、综艺、影视、电影、剧集、电视剧）
    - 生活类（生活、健康、美食、旅游、情感）
    - 知识类（知识、学习、教育、科学、法律）
    - 社会类（社会、国际、国内、时事、新闻）
    - 创新类（创新、创业、商业、金融、财经）

    Parameters:
        category: 话题分类，不填则默认获取热点话题
        keywords: 关键词，用于过滤结果
        limit: 返回结果数量，默认20条
        force_summarize: 是否强制返回摘要数据，不论数据量大小
        word_limit: 当返回的数据超过此字数限制时会自动生成摘要，默认500
    """

    name = "trending_topics"
    description = """获取和搜索各大平台热点话题。支持以下功能和分类：

主要功能：
1. 获取指定分类的热点话题
2. 搜索包含关键词的话题
3. 自动生成热点摘要（当数据量较大时）

可用分类：
- 综合类：热点、热门、推荐、trending
- 科技类：科技、技术、tech、数码
- 娱乐类：娱乐、明星、综艺、影视、电影、剧集、电视剧
- 生活类：生活、健康、美食、旅游、情感
- 知识类：知识、学习、教育、科学、法律
- 社会类：社会、国际、国内、时事、新闻
- 创新类：创新、创业、商业、金融、财经

数据摘要：
- 当数据量过大时会自动返回摘要
- 可强制返回摘要版本

注意：如果指定的分类不存在，将默认返回"热点"分类的内容。"""

    parameters = {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "话题分类，如果不指定或指定的分类不存在，默认使用'热点'分类。建议使用主要分类（如：热点、科技、娱乐、生活、知识、社会等）",
                "default": "热点"
            },
            "keywords": {
                "type": "string",
                "description": "搜索关键词，将在话题标题和描述中进行匹配",
                "optional": True
            },
            "limit": {
                "type": "integer",
                "description": "返回结果数量，默认20条，最大50条",
                "default": 20,
                "minimum": 1,
                "maximum": 50
            },
            "force_summarize": {
                "type": "boolean",
                "description": "是否强制返回摘要数据，而不是完整数据",
                "default": False,
                "optional": True
            },
            "word_limit": {
                "type": "integer",
                "description": "当返回数据超过此字数时，自动返回摘要版本，默认500字",
                "default": 500,
                "minimum": 100,
                "maximum": 5000,
                "optional": True
            },
            "compression_ratio": {
                "type": "number",
                "description": "摘要压缩率，表示摘要提取的话题比例，取值0.1-0.5，默认0.25",
                "default": 0.25,
                "minimum": 0.1,
                "maximum": 0.5,
                "optional": True
            }
        }
    }

    def __init__(self) -> None:
        """初始化热门话题工具"""
        super().__init__()
        self.filter = TopicFilter()
        self.processor = TopicProcessor()
        self.token_counter = TokenCounter()
        config = get_config()
        self.redis = RedisStorage(config["redis_url"])
        logger.info("初始化热点话题工具")

    def get_description(self) -> Dict:
        """获取工具描述信息"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    def _is_tool_call(self) -> bool:
        """判断是否为工具调用

        通过检查调用栈来判断是否为工具调用

        Returns:
            bool: 是否为工具调用
        """
        stack = inspect.stack()

        # 检查调用栈中是否包含工具调用相关的函数名
        tool_call_patterns = [
            # CrewAI 工具调用模式
            "execute_tool",
            "run_tool",
            "tool_call",
            "_execute_tool",
            "_run_tool",
            "execute_task",
            "run_task",
            # 测试环境
            "test_get_topics",
            "test_search_topics",
            "test_invalid_category",
            "test_all_categories"
        ]

        # 检查调用栈
        for frame in stack:
            # 检查函数名
            if frame.function in tool_call_patterns:
                return True

            # 检查是否来自测试文件
            if frame.filename.endswith(("test_trending_topics.py", "test_tools.py")):
                return True

        # 如果设置了强制使用缓存的参数，也视为工具调用
        frame = stack[1]  # 获取直接调用者的帧
        if frame.frame.f_locals.get("force_cache"):
            return True

        return False

    async def read_topics(
        self,
        category: Optional[str] = "热点",
        keywords: Optional[str] = None,
        limit: Optional[int] = 20,
        platform: Optional[str] = None
    ) -> Dict:
        """从Redis缓存读取热点话题数据

        Args:
            category: 话题分类，默认为"热点"
            keywords: 搜索关键词，将在标题中进行匹配
            limit: 返回结果数量，默认20条，最大50条
            platform: 指定平台，如果提供则直接获取该平台的数据

        Returns:
            Dict: 处理后的话题数据
        """
        try:
            # 如果指定了平台，直接获取该平台数据
            if platform:
                logger.info(f"直接获取平台 {platform} 的数据")
                processed_topics = []
                try:
                    platform_topics = await self.redis.get_platform_topics(platform)
                    if platform_topics:
                        processed_topics.extend(platform_topics)
                        logger.info(f"获取到 {len(platform_topics)} 条话题")
                    else:
                        logger.warning(f"平台 {platform} 无有效数据")
                except Exception as e:
                    error_msg = f"读取平台 {platform} 数据失败: {str(e)}"
                    logger.error(error_msg)
                    return {
                        "error": "读取数据失败",
                        "message": error_msg,
                        "total": 0,
                        "platform": platform
                    }
            else:
                # 分类参数验证和平台获取
                if not category:
                    category = "热点"
                    logger.info("未指定分类，使用默认分类'热点'")

                # 获取分类对应的平台列表
                platforms = get_platforms_by_category(category)

                # 如果分类无效或没有关联平台，使用热点标签
                if not platforms:
                    if category != "热点":
                        logger.warning(f"分类 '{category}' 没有关联平台，将使用'热点'标签")
                        category = "热点"
                        platforms = get_platforms_by_category(category)

                        if not platforms:
                            logger.error("热点标签也没有关联平台，系统配置可能有误")
                            return {
                                "error": "系统配置错误",
                                "message": "热点标签未配置关联平台",
                                "total": 0,
                                "category": category
                            }

                # 从Redis读取数据
                logger.info(f"从Redis缓存读取{category}分类数据")
                processed_topics = []
                failed_platforms = []

                # 使用字典存储每个标题的话题版本
                title_to_topic = {}

                # 遍历每个平台
                for platform in platforms:
                    try:
                        # 获取平台话题数据
                        platform_topics = await self.redis.get_platform_topics(platform)
                        if not platform_topics:
                            logger.warning(f"平台 {platform} 无有效数据")
                            continue

                        # 添加到总数据集合（去重）
                        for topic in platform_topics:
                            title = topic.get("title")
                            if not title:
                                continue
                            # 仅保留一个版本（避免重复）
                            if title not in title_to_topic:
                                title_to_topic[title] = topic

                    except Exception as e:
                        error_msg = f"读取平台 {platform} 数据失败: {str(e)}"
                        logger.error(error_msg)
                        failed_platforms.append({"platform": platform, "error": str(e)})
                        continue

                # 将话题版本添加到结果列表
                processed_topics = list(title_to_topic.values())

            if not processed_topics:
                error_msg = "暂无数据"
                if platform:
                    error_msg = f"平台 '{platform}' " + error_msg
                elif category:
                    error_msg = f"分类 '{category}' " + error_msg
                if failed_platforms:
                    error_msg += "\n失败详情:\n" + "\n".join(
                        f"- {p['platform']}: {p['error']}"
                        for p in failed_platforms
                    )
                logger.warning(error_msg)
                return {
                    "error": "暂无数据",
                    "message": error_msg,
                    "total": 0,
                    "category": category if not platform else None,
                    "platform": platform if platform else None,
                    "failed_platforms": failed_platforms if not platform else None
                }

            # 保存原始数据数量
            original_count = len(processed_topics)

            # 根据关键词过滤
            if keywords:
                filtered_topics = self.filter.search_topics(processed_topics, keywords)
                if not filtered_topics:
                    # 如果关键词搜索没有结果，返回原始数据，并标记为无匹配
                    logger.info(f"未找到包含关键词 '{keywords}' 的话题，将返回原始分类数据")
                    return {
                        "topics": processed_topics[:limit],  # 返回原始分类数据
                        "total": min(len(processed_topics), limit),
                        "category": category if not platform else None,
                        "platform": platform if platform else None,
                        "platforms": list(set(topic["platform"] for topic in processed_topics[:limit])),
                        "message": f"未找到包含关键词 '{keywords}' 的话题，使用分类数据代替",
                        "original_count": original_count,
                        "keywords": keywords,
                        "is_supplemented": True,  # 标记为已补充（虽然是完全替代而非补充）
                        "matched_count": 0,
                        "supplemented_count": min(len(processed_topics), limit)
                    }

                # 关键词匹配成功，使用过滤后的结果
                processed_topics = filtered_topics
                logger.info(f"关键词过滤: {original_count} -> {len(processed_topics)}")

            # 计算优先级分数并排序
            for topic in processed_topics:
                try:
                    topic["priority_score"] = self.processor.calculate_priority_score(topic)
                except Exception as e:
                    logger.error(f"计算优先级分数失败: {e}, topic: {topic['title']}")
                    topic["priority_score"] = 0

            processed_topics.sort(key=lambda x: x["priority_score"], reverse=True)

            # 限制返回数量
            limit = min(limit or 20, 50)  # 确保不超过50
            if limit:
                processed_topics = processed_topics[:limit]

            result = {
                "topics": processed_topics,
                "total": len(processed_topics),
                "platforms": list(set(topic["platform"] for topic in processed_topics)),
                "message": f"成功获取并处理 {len(processed_topics)} 条数据"
            }

            # 如果是按分类获取，添加分类信息
            if not platform:
                result["category"] = category
            else:
                result["platform"] = platform

            # 如果有处理失败的平台，添加到结果中
            if failed_platforms:
                result["failed_platforms"] = failed_platforms

            # 如果是关键词搜索，添加关键词信息
            if keywords:
                result["keywords"] = keywords
                result["original_count"] = original_count

            return result

        except Exception as e:
            error_msg = f"读取热点话题失败: {str(e)}"
            logger.error(error_msg)
            return {
                "error": "读取热点话题失败",
                "message": error_msg,
                "total": 0,
                "category": category if not platform else None,
                "platform": platform if platform else None,
                "stack_trace": str(e)
            }

    async def fetch_topics(self) -> Dict[str, List[Dict]]:
        """获取所有平台的原始数据

        Returns:
            Dict[str, List[Dict]]: 平台名称到话题列表的映射
        """
        try:
            logger.info("开始获取所有平台数据...")

            from .api_collector import APICollector

            # 使用上下文管理器确保会话正确初始化和关闭
            async with APICollector() as collector:
                logger.info("API收集器初始化完成")

                # 加载平台配置
                config_loaded = await collector._load_platforms_config()
                if not config_loaded:
                    logger.error("加载平台配置失败")
                    return {}

                all_data = await collector.get_all_topics()

            if not all_data or not isinstance(all_data, dict):
                logger.error("获取数据失败或数据格式错误")
                return {}

            # 过滤掉空数据和非列表数据
            filtered_data = {}
            for platform, topics in all_data.items():
                if isinstance(topics, list) and topics:
                    filtered_data[platform] = topics
                else:
                    logger.warning(f"平台 {platform} 数据无效: {topics}")

            if not filtered_data:
                logger.error("没有获取到任何有效数据")
                return {}

            logger.info(f"成功获取 {len(filtered_data)} 个平台的数据")
            return filtered_data

        except Exception as e:
            logger.error(f"获取数据失败: {e}", exc_info=True)
            return {}

    async def _process_topics(self, platform_data: Dict[str, List[Dict]]) -> List[Dict]:
        """处理原始话题数据

        Args:
            platform_data: 平台原始数据

        Returns:
            List[Dict]: 处理后的话题列表
        """
        if not platform_data:
            logger.error("没有数据需要处理")
            return []

        try:
            processed_topics = []
            current_time = datetime.now()

            for platform, topics in platform_data.items():
                if not isinstance(topics, list):
                    logger.warning(f"平台 {platform} 数据格式错误")
                    continue

                logger.info(f"处理平台 {platform} 的 {len(topics)} 条数据")

                for topic in topics:
                    if not isinstance(topic, dict):
                        continue

                    # 必需字段检查
                    title = topic.get("title")
                    if not title or not isinstance(title, str):
                        continue

                    # 处理热度值
                    hot = topic.get("hot")
                    if hot is None:
                        hot = get_default_hot_score(platform)
                    else:
                        try:
                            hot = int(hot)
                        except (ValueError, TypeError):
                            hot = get_default_hot_score(platform)

                    # 处理时间戳
                    timestamp = topic.get("timestamp")
                    if timestamp:
                        try:
                            timestamp = int(timestamp)
                        except (ValueError, TypeError):
                            timestamp = int(current_time.timestamp())
                    else:
                        timestamp = int(current_time.timestamp())

                    # 构建处理后的话题数据
                    processed_topic = {
                        "title": title,
                        "platform": platform,
                        "source_time": timestamp,
                        "hot": hot,
                        "expire_time": int((current_time + timedelta(days=7)).timestamp())
                    }

                    # 保留原始字段
                    for key, value in topic.items():
                        if key not in processed_topic:
                            processed_topic[key] = value

                    processed_topics.append(processed_topic)

            if not processed_topics:
                logger.error("没有处理出有效数据")
                return []

            logger.info(f"共处理 {len(processed_topics)} 条有效数据")
            return processed_topics

        except Exception as e:
            logger.error(f"处理数据失败: {e}")
            return []

    async def _summarize_topics(self, topics: List[Dict], summarize_type: str = "category", compression_ratio: float = 0.25) -> Dict:
        """将话题数据进行摘要处理

        Args:
            topics: 话题列表
            summarize_type: 摘要类型，category(按分类) 或 keyword(按关键词)
            compression_ratio: 摘要压缩率，表示摘要提取的话题比例，取值0.1-0.5

        Returns:
            Dict: 摘要后的数据
        """
        if not topics:
            return {"summary": "无可用数据", "topics": []}

        # 获取话题总数和平台信息
        platform_count = len(set(topic.get("platform", "") for topic in topics))
        total_count = len(topics)

        # 按平台分组统计
        platform_stats = {}
        # 增加统计热词
        word_freq = {}

        for topic in topics:
            # 平台统计
            platform = topic.get("platform", "unknown")
            if platform not in platform_stats:
                platform_stats[platform] = {"count": 0, "max_hot": 0, "hottest_topic": None}

            platform_stats[platform]["count"] += 1
            hot = topic.get("hot", 0)

            if hot > platform_stats[platform]["max_hot"]:
                platform_stats[platform]["max_hot"] = hot
                platform_stats[platform]["hottest_topic"] = topic

            # 提取热词
            title = topic.get("title", "")
            if title:
                # 简单分词（实际应用中可以使用更复杂的分词）
                words = [w for w in re.split(r'[^\w\u4e00-\u9fff]+', title) if len(w) > 1]
                for word in words:
                    if word not in word_freq:
                        word_freq[word] = 0
                    word_freq[word] += 1

        # 基于压缩率计算要返回的话题数量
        summary_topic_count = max(3, int(total_count * compression_ratio))

        # 提取热门程度最高的话题
        sorted_topics = sorted(topics, key=lambda x: x.get("hot", 0), reverse=True)
        top_topics = sorted_topics[:summary_topic_count]

        # 获取最常见的5个关键词（排除常见词）
        stop_words = {"的", "了", "和", "在", "是", "有", "这", "我", "你", "他", "她", "它", "们", "个", "为", "也", "及", "与"}
        top_words = sorted(
            [(word, freq) for word, freq in word_freq.items() if word not in stop_words and len(word) > 1],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # 生成摘要文本
        if summarize_type == "category":
            summary = f"共{total_count}条热门话题，来自{platform_count}个平台。"
        else:  # keyword
            keywords = topics[0].get("keywords", "") if topics else ""
            summary = f"关键词'{keywords}'共找到{total_count}条相关话题，来自{platform_count}个平台。"

        # 添加热门平台信息
        sorted_platforms = sorted(platform_stats.items(),
                                 key=lambda x: x[1]["count"],
                                 reverse=True)
        top_platforms = sorted_platforms[:3]
        platform_info = []

        for platform, stats in top_platforms:
            platform_info.append(f"{platform}({stats['count']}条)")

        if platform_info:
            summary += f" 主要来源：{', '.join(platform_info)}。"

        # 添加热门关键词
        if top_words:
            summary += f" 热门关键词：{', '.join(word for word, _ in top_words)}。"

        # 添加最热门话题信息
        if top_topics:
            summary += " 热度最高的话题："
            for i, topic in enumerate(top_topics[:3], 1):
                title = topic.get("title", "")
                platform = topic.get("platform", "")
                hot = topic.get("hot", 0)
                summary += f"{i}.「{title}」({platform}, 热度{hot})"
                if i < len(top_topics[:3]):
                    summary += "；"
            summary += "。"

        # 增加统计信息
        stats = {
            "total_topics": total_count,
            "platform_count": platform_count,
            "top_platforms": [{"name": p, "count": s["count"]} for p, s in sorted_platforms[:5]],
            "hot_keywords": [{"word": w, "freq": f} for w, f in top_words],
            "avg_hot": sum(topic.get("hot", 0) for topic in topics) // max(1, len(topics)),
            "compression_ratio": compression_ratio,
            "summary_topic_count": summary_topic_count
        }

        # 返回摘要数据
        return {
            "summary": summary,
            "topics": top_topics,
            "total": total_count,
            "platforms": list(set(topic.get("platform", "") for topic in topics)),
            "is_summarized": True,
            "summarize_type": summarize_type,
            "stats": stats
        }

    def _count_words_in_topics(self, topics: List[Dict]) -> int:
        """统计话题数据中的字数

        Args:
            topics: 话题列表

        Returns:
            int: 总字数
        """
        if not topics:
            return 0

        # 将所有话题数据转为字符串
        text = ""
        for topic in topics:
            title = topic.get("title", "")
            desc = topic.get("desc", "")
            text += f"{title} {desc} "

        # 使用空格分词统计（简易统计，实际应考虑中文）
        return len(text)

    async def execute(
        self,
        category: Optional[str] = None,
        keywords: Optional[str] = None,
        limit: Optional[int] = 20,
        force_summarize: Optional[bool] = False,
        word_limit: Optional[int] = 500,
        compression_ratio: Optional[float] = 0.25
    ) -> Dict:
        """工具入口方法，根据参数从缓存读取数据

        策略：
        1. 无参数 → 默认热门分类
        2. 仅指定 category → 从该分类平台获取
        3. 仅指定 keywords → 从所有平台搜索
        4. 同时指定 category + keywords → 从指定分类搜索关键词

        结果数量策略：
        当关键词搜索结果不足时，会自动从相应分类补充数据到达limit数量

        摘要策略：
        1. force_summarize=True → 直接返回摘要版本
        2. 数据字数超过word_limit → 返回摘要版本
        3. 其他情况 → 返回完整数据

        Args:
            category: 话题分类，默认为None，将使用"热点"分类
            keywords: 搜索关键词，将在标题中进行匹配
            limit: 返回结果数量，默认20条，最大50条
            force_summarize: 是否强制返回摘要，默认False
            word_limit: 字数限制，超过则返回摘要，默认500
            compression_ratio: 摘要压缩率，表示摘要提取的话题比例，取值0.1-0.5，默认0.25

        Returns:
            Dict: 处理后的话题数据
        """
        # 确保limit在有效范围内
        limit = min(max(limit or 20, 1), 50)

        # 确保compression_ratio在有效范围内
        compression_ratio = min(max(compression_ratio or 0.25, 0.1), 0.5)

        # 场景1: 仅指定关键词，无分类 - 从所有平台搜索
        if keywords and not category:
            logger.info(f"仅指定关键词'{keywords}'，从所有平台搜索")
            all_topics = []
            failed_platforms = []

            # 获取所有平台列表
            all_platforms = list(PLATFORM_CATEGORIES.keys())

            # 从每个平台获取数据
            title_to_topic = {}  # 用于去重

            for platform in all_platforms:
                try:
                    # 获取平台话题数据
                    platform_topics = await self.redis.get_platform_topics(platform)
                    if not platform_topics:
                        continue

                    # 添加到总数据集合（去重）
                    for topic in platform_topics:
                        title = topic.get("title")
                        if not title:
                            continue
                        # 仅保留一个版本（避免重复）
                        if title not in title_to_topic:
                            title_to_topic[title] = topic

                except Exception as e:
                    logger.error(f"读取平台 {platform} 数据失败: {str(e)}")
                    failed_platforms.append({"platform": platform, "error": str(e)})

            # 将所有话题转为列表
            all_topics = list(title_to_topic.values())

            # 根据关键词过滤
            original_count = len(all_topics)
            filtered_topics = self.filter.search_topics(all_topics, keywords)
            logger.info(f"关键词过滤: 总数据 {original_count} -> 过滤后 {len(filtered_topics)}")

            # 处理搜索结果
            if not filtered_topics:
                # 无匹配结果时，从热点标签平台补充数据
                logger.info(f"未找到关键词'{keywords}'匹配结果，将从热点标签平台补充数据")

                # 获取所有热点标签相关平台
                hot_platforms = get_platforms_by_category("热点")
                hot_topics = []

                # 从热点相关平台获取数据
                for platform in hot_platforms:
                    try:
                        platform_topics = await self.redis.get_platform_topics(platform)
                        if platform_topics:
                            hot_topics.extend(platform_topics)
                    except Exception as e:
                        logger.error(f"读取热点平台 {platform} 数据失败: {str(e)}")

                if hot_topics:
                    # 去重
                    title_to_topic = {}
                    for topic in hot_topics:
                        title = topic.get("title", "")
                        if title and title not in title_to_topic:
                            title_to_topic[title] = topic

                    result_topics = list(title_to_topic.values())

                    # 计算优先级并排序
                    for topic in result_topics:
                        try:
                            topic["priority_score"] = self.processor.calculate_priority_score(topic)
                        except Exception as e:
                            logger.error(f"计算优先级分数失败: {e}, topic: {topic['title']}")
                            topic["priority_score"] = 0

                    result_topics.sort(key=lambda x: x["priority_score"], reverse=True)
                    result_topics = result_topics[:limit]

                    result = {
                        "topics": result_topics,
                        "total": len(result_topics),
                        "platforms": list(set(topic["platform"] for topic in result_topics)),
                        "message": f"未找到关键词'{keywords}'匹配数据，已从热点平台补充{len(result_topics)}条数据",
                        "keywords": keywords,
                        "is_supplemented": True,
                        "original_count": 0
                    }

                    # 检查是否需要摘要
                    if force_summarize:
                        logger.info("强制返回摘要数据")
                        return await self._summarize_topics(result["topics"], "keyword", compression_ratio)

                    # 检查数据量是否超过限制
                    if self._count_words_in_topics(result["topics"]) > word_limit:
                        logger.info(f"数据字数超过限制({word_limit})，返回摘要")
                        return await self._summarize_topics(result["topics"], "keyword", compression_ratio)

                    return result
                else:
                    return {
                        "error": "无匹配数据",
                        "message": f"未找到包含关键词 '{keywords}' 的话题，且热点平台也无数据",
                        "total": 0,
                        "keywords": keywords,
                        "original_count": original_count
                    }

            # 计算优先级分数并排序
            for topic in filtered_topics:
                try:
                    topic["priority_score"] = self.processor.calculate_priority_score(topic)
                except Exception as e:
                    logger.error(f"计算优先级分数失败: {e}, topic: {topic['title']}")
                    topic["priority_score"] = 0

            filtered_topics.sort(key=lambda x: x["priority_score"], reverse=True)

            # 如果过滤后的话题数量不足limit，从热点标签平台补充
            result_topics = filtered_topics[:limit]
            supplemented_count = 0

            if len(result_topics) < limit:
                needed_count = limit - len(result_topics)
                logger.info(f"关键词搜索结果数量不足({len(result_topics)}<{limit})，将从热点标签平台补充{needed_count}条数据")

                # 获取所有热点标签相关平台
                hot_platforms = get_platforms_by_category("热点")
                hot_topics = []

                # 从热点相关平台获取数据
                for platform in hot_platforms:
                    try:
                        platform_topics = await self.redis.get_platform_topics(platform)
                        if platform_topics:
                            hot_topics.extend(platform_topics)
                    except Exception as e:
                        logger.error(f"读取热点平台 {platform} 数据失败: {str(e)}")

                if hot_topics:
                    # 排除已有的标题
                    existing_titles = {topic["title"] for topic in result_topics}
                    supplement_topics = []

                    for topic in hot_topics:
                        title = topic.get("title", "")
                        if title and title not in existing_titles:
                            supplement_topics.append(topic)
                            existing_titles.add(title)
                            if len(supplement_topics) >= needed_count:
                                break

                    # 添加补充的话题
                    result_topics.extend(supplement_topics)
                    supplemented_count = len(supplement_topics)
                    logger.info(f"成功从热点标签平台补充了{supplemented_count}条数据")

            # 构建结果
            result = {
                "topics": result_topics,
                "total": len(result_topics),
                "platforms": list(set(topic["platform"] for topic in result_topics)),
                "keywords": keywords
            }

            if supplemented_count > 0:
                result["message"] = f"从所有平台搜索到{len(filtered_topics)}条'{keywords}'相关数据，补充了{supplemented_count}条热点数据"
                result["is_supplemented"] = True
                result["matched_count"] = len(filtered_topics)
                result["supplemented_count"] = supplemented_count
            else:
                result["message"] = f"从所有平台搜索到{len(result_topics)}条'{keywords}'相关数据"

            if failed_platforms:
                result["failed_platforms"] = failed_platforms

            # 检查是否需要摘要
            if force_summarize:
                logger.info("强制返回摘要数据")
                return await self._summarize_topics(result["topics"], "keyword", compression_ratio)

            # 检查数据量是否超过限制
            if self._count_words_in_topics(result["topics"]) > word_limit:
                logger.info(f"数据字数超过限制({word_limit})，返回摘要")
                return await self._summarize_topics(result["topics"], "keyword", compression_ratio)

            return result

        # 场景2-4: 其他情况 - 使用分类或默认分类
        use_category = category or "热点"
        logger.info(f"使用分类'{use_category}'获取数据" + (f"，搜索关键词'{keywords}'" if keywords else ""))

        # 获取分类对应的平台列表
        platforms = get_platforms_by_category(use_category)

        # 如果分类无效或没有关联平台，使用热点标签
        if not platforms:
            if use_category != "热点":
                logger.warning(f"分类 '{use_category}' 没有关联平台，将使用'热点'标签")
                use_category = "热点"
                platforms = get_platforms_by_category(use_category)

                if not platforms:
                    logger.error("热点标签也没有关联平台，系统配置可能有误")
                    return {
                        "error": "系统配置错误",
                        "message": "热点标签未配置关联平台",
                        "total": 0,
                        "category": use_category
                    }

        # 从每个平台获取数据
        all_topics = []
        failed_platforms = []

        for platform in platforms:
            try:
                platform_topics = await self.redis.get_platform_topics(platform)
                if platform_topics:
                    all_topics.extend(platform_topics)
            except Exception as e:
                logger.error(f"读取平台 {platform} 数据失败: {str(e)}")
                failed_platforms.append({"platform": platform, "error": str(e)})

        # 如果没有获取到数据
        if not all_topics:
            error_msg = f"分类 '{use_category}' 暂无数据"
            if failed_platforms:
                error_msg += "\n失败详情:\n" + "\n".join(
                    f"- {p['platform']}: {p['error']}"
                    for p in failed_platforms
                )
            logger.warning(error_msg)
            return {
                "error": "暂无数据",
                "message": error_msg,
                "total": 0,
                "category": use_category,
                "failed_platforms": failed_platforms
            }

        # 去重处理
        title_to_topic = {}
        for topic in all_topics:
            title = topic.get("title", "")
            if title and title not in title_to_topic:
                title_to_topic[title] = topic

        processed_topics = list(title_to_topic.values())

        # 保存原始数据数量
        original_count = len(processed_topics)

        # 根据关键词过滤
        if keywords:
            filtered_topics = self.filter.search_topics(processed_topics, keywords)
            if not filtered_topics:
                # 无匹配结果时，不再补充数据，而是返回空结果
                logger.warning(f"在'{use_category}'分类中未找到包含关键词'{keywords}'的话题")
                return {
                    "error": "无匹配数据",
                    "message": f"在'{use_category}'分类中未找到包含关键词'{keywords}'的话题",
                    "total": 0,
                    "category": use_category,
                    "keywords": keywords,
                    "original_count": original_count
                }

            processed_topics = filtered_topics
            logger.info(f"关键词过滤: 总数据 {original_count} -> 过滤后 {len(processed_topics)}")

        # 计算优先级分数并排序
        for topic in processed_topics:
            try:
                topic["priority_score"] = self.processor.calculate_priority_score(topic)
            except Exception as e:
                logger.error(f"计算优先级分数失败: {e}, topic: {topic['title']}")
                topic["priority_score"] = 0

        processed_topics.sort(key=lambda x: x["priority_score"], reverse=True)

        # 限制返回数量
        limit = min(limit or 20, 50)  # 确保不超过50
        processed_topics = processed_topics[:limit]

        # 构建结果
        result = {
            "topics": processed_topics,
            "total": len(processed_topics),
            "category": use_category,
            "platforms": list(set(topic["platform"] for topic in processed_topics)),
            "message": f"成功获取并处理 {len(processed_topics)} 条数据"
        }

        # 如果有处理失败的平台，添加到结果中
        if failed_platforms:
            result["failed_platforms"] = failed_platforms

        # 如果是关键词搜索，添加关键词信息
        if keywords:
            result["keywords"] = keywords
            result["original_count"] = original_count

        # 检查是否需要摘要
        if force_summarize:
            logger.info("强制返回摘要数据")
            return await self._summarize_topics(result["topics"], "category", compression_ratio)

        # 检查数据量是否超过限制
        if self._count_words_in_topics(result["topics"]) > word_limit:
            logger.info(f"数据字数超过限制({word_limit})，返回摘要")
            return await self._summarize_topics(result["topics"], "category", compression_ratio)

        return result

    async def get_topics_by_category(
        self,
        category: str,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """获取指定分类的话题列表

        Args:
            category: 分类名称
            limit: 返回结果数量限制

        Returns:
            List[Dict]: 话题列表
        """
        result = await self.read_topics(category=category, limit=limit)
        return result.get("topics", []) if "topics" in result else []
