"""选题团队工具集

这个模块包含了选题团队所需的工具。专注于从热搜平台获取话题信息，为后续写作提供方向。
工具被组织为一个类，并通过crewai的工具装饰器暴露给智能体。
"""
from typing import List, Dict, Any, Optional
from crewai.tools import tool, BaseTool
from pydantic import BaseModel, Field
from core.tools.trending_tools import TrendingTopics
from core.config import Config


class TopicTools:
    """选题团队工具集

    这个类包含了选题团队需要的核心工具，专注于热搜话题的获取和分析。
    遵循最小开发原则，当前阶段仅实现热搜相关功能。
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化工具集

        Args:
            config: 配置对象，如果为None则创建默认配置
        """
        # 加载配置
        self.config = config or Config()

        # 初始化核心工具实例 - 专注于热搜工具
        self.trending_tools = TrendingTopics()

        # 注册工具方法 - 关键修复：将实例方法转换为独立函数
        # 由于crewai工具要求函数而非方法，我们需要创建所有工具方法的独立函数版本
        self.get_trending_topics = self._create_bound_tool(self.get_trending_topics_method)
        self.get_topic_details = self._create_bound_tool(self.get_topic_details_method)
        self.recommend_topics = self._create_bound_tool(self.recommend_topics_method)

    def _create_bound_tool(self, method):
        """创建绑定工具函数

        将实例方法绑定到实例上，确保self参数正确传递

        Args:
            method: 实例方法

        Returns:
            绑定的函数，可作为工具使用
        """
        # 将方法的__doc__和其他属性复制到绑定函数
        bound_func = lambda *args, **kwargs: method(*args, **kwargs)
        bound_func.__doc__ = method.__doc__
        bound_func.__name__ = method.__name__
        bound_func.__qualname__ = method.__qualname__

        # 保持工具装饰器属性
        if hasattr(method, "_crewai_tool"):
            bound_func._crewai_tool = method._crewai_tool

        return bound_func

    # ======== 热搜话题工具 ========

    @tool("热搜话题获取工具")
    def get_trending_topics_method(self, category: Optional[str] = None, keywords: Optional[str] = None, limit: int = 20) -> str:
        """获取各大平台热搜话题，支持指定分类和关键词过滤。

        Args:
            category: 可选的分类名称，例如"科技"、"娱乐"、"教育"等
            keywords: 可选的关键词，用于过滤话题
            limit: 返回的话题数量上限，默认为20

        Returns:
            str: 包含热搜话题列表的文本
        """
        return self.trending_tools.execute(category=category, keywords=keywords, limit=limit)

    @tool("话题详情获取工具")
    def get_topic_details_method(self, topic_id: str) -> str:
        """获取特定热搜话题的详细信息。

        Args:
            topic_id: 话题ID或话题完整名称

        Returns:
            str: 包含话题详细信息的文本
        """
        return self.trending_tools.execute(action="details", topic_id=topic_id)

    @tool("话题推荐工具")
    def recommend_topics_method(self, target_audience: Optional[str] = None, content_type: Optional[str] = None, limit: int = 5) -> str:
        """基于目标受众和内容类型推荐合适的热搜话题。

        Args:
            target_audience: 目标受众群体，如"年轻人"、"职场人士"、"学生"等
            content_type: 内容类型，如"短视频"、"文章"、"图文"等
            limit: 推荐话题数量

        Returns:
            str: 包含推荐话题及简要分析的文本
        """
        return self.trending_tools.execute(action="recommend", target_audience=target_audience,
                                          content_type=content_type, limit=limit)
