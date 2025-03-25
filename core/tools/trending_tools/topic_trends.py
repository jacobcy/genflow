"""热点话题工具

提供热点话题的获取、过滤和处理功能。
"""
import logging
from typing import Dict, List, Optional
import inspect
from datetime import datetime, timedelta

from .api_collector import APICollector
from .utils import TopicProcessor, TopicFilter, TokenCounter
from .platform_categories import CATEGORY_TAGS, get_platforms_by_category
from .redis_storage import RedisStorage
from .config import get_config
from .platform_weights import get_platform_weight, get_default_hot_score

logger = logging.getLogger(__name__)

class TrendingTopics:
    """热点话题工具类"""

    name = "trending_topics"
    description = """获取和搜索各大平台热点话题。支持以下功能和分类：

主要功能：
1. 获取指定分类的热点话题
2. 搜索包含关键词的话题
3. 自动生成热点摘要（当数据量较大时）

可用分类：
- 综合类：热点、时事、资讯、深度
- 科技类：科技、互联网、开发、编程、数码
- 娱乐类：娱乐、游戏、二次元、电竞
- 生活类：生活、购物、优惠、消费
- 知识类：知识、科普、学习、问答
- 社会类：社会、国际、评论
- 创新类：创新、创业、开源、效率

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
            }
        }
    }

    def __init__(self):
        """初始化工具类"""
        self.collector = APICollector()
        self.processor = TopicProcessor()
        self.filter = TopicFilter()
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

                # 如果分类无效或没有关联平台，使用热点分类
                if not platforms:
                    if category != "热点":
                        logger.warning(f"分类 '{category}' 没有关联平台，将使用'热点'分类")
                        category = "热点"
                        platforms = get_platforms_by_category(category)

                        if not platforms:
                            logger.error("热点分类也没有关联平台，系统配置可能有误")
                            return {
                                "error": "系统配置错误",
                                "message": "热点分类未配置关联平台",
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

                        # 处理每个话题
                        for topic in platform_topics:
                            title = topic.get("title")
                            if not title:
                                continue

                            # 如果标题已存在，跳过
                            if title in title_to_topic:
                                continue
                            else:
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

            # 根据关键词过滤
            if keywords:
                original_count = len(processed_topics)
                processed_topics = self.filter.search_topics(processed_topics, keywords)
                if not processed_topics:
                    return {
                        "error": "无匹配数据",
                        "message": f"未找到包含关键词 '{keywords}' 的话题",
                        "total": 0,
                        "category": category if not platform else None,
                        "platform": platform if platform else None,
                        "original_count": original_count
                    }
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
            all_data = await self.collector.get_all_topics()

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
            logger.error(f"获取数据失败: {e}")
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
                        "timestamp": timestamp,
                        "hot": hot,
                        "fetch_time": int(current_time.timestamp()),
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

    async def execute(
        self,
        category: Optional[str] = "热点",
        keywords: Optional[str] = None,
        limit: Optional[int] = 20
    ) -> Dict:
        """工具入口方法，默认从缓存读取数据

        Args:
            category: 话题分类，默认为"热点"
            keywords: 搜索关键词，将在标题中进行匹配
            limit: 返回结果数量，默认20条，最大50条

        Returns:
            Dict: 处理后的话题数据
        """
        # 先尝试搜索
        search_result = await self.read_topics(category, keywords, limit)

        # 如果有关键词搜索且结果数量小于limit,则用分类数据补足
        if keywords and search_result.get("total", 0) < limit:
            logger.info(f"关键词'{keywords}'搜索结果数量({search_result.get('total', 0)})小于limit({limit}),使用'{category}'分类数据补足")

            # 获取分类数据
            category_result = await self.read_topics(category=category, limit=limit)
            if "topics" in category_result:
                # 获取已有的搜索结果topics
                existing_topics = search_result.get("topics", [])

                # 从分类数据中排除已有的话题(根据标题去重)
                existing_titles = {topic["title"] for topic in existing_topics}
                supplement_topics = [
                    topic for topic in category_result["topics"]
                    if topic["title"] not in existing_titles
                ]

                # 补足到limit数量
                needed_count = limit - len(existing_topics)
                if needed_count > 0:
                    existing_topics.extend(supplement_topics[:needed_count])

                    # 更新结果
                    search_result["topics"] = existing_topics
                    search_result["total"] = len(existing_topics)
                    search_result["message"] = f"搜索到 {len(existing_topics)} 条数据(包含 {needed_count} 条分类补充数据)"

        return search_result

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
