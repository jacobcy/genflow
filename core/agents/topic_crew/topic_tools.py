"""选题团队工具集

这个模块包含了选题团队所需的工具。专注于从热搜平台获取话题信息，为后续写作提供方向。
工具被组织为一个类，并通过crewai的工具装饰器暴露给智能体。
"""
from typing import List, Dict, Any, Optional, Type
from crewai.tools import tool, BaseTool
from pydantic import BaseModel, Field
from core.tools.trending_tools import TrendingTopics
from core.config import Config


class TrendingTopicsInput(BaseModel):
    """热搜话题获取工具的输入架构"""
    category: Optional[str] = Field(None, description="可选的分类名称，例如'科技'、'娱乐'、'教育'等")
    keywords: Optional[str] = Field(None, description="可选的关键词，用于过滤话题")
    limit: int = Field(20, description="返回的话题数量上限，默认为20")


class TopicDetailsInput(BaseModel):
    """话题详情获取工具的输入架构"""
    topic_id: str = Field(..., description="话题ID或话题完整名称")


class RecommendTopicsInput(BaseModel):
    """话题推荐工具的输入架构"""
    target_audience: Optional[str] = Field(None, description="目标受众群体，如'年轻人'、'职场人士'、'学生'等")
    content_type: Optional[str] = Field(None, description="内容类型，如'短视频'、'文章'、'图文'等")
    limit: int = Field(5, description="推荐话题数量，默认为5")


class GetTrendingTopicsTool(BaseTool):
    """热搜话题获取工具"""
    name: str = "热搜话题获取工具"
    description: str = "获取各大平台热搜话题，支持指定分类和关键词过滤。"
    args_schema: Type[BaseModel] = TrendingTopicsInput

    # 允许额外属性
    model_config = {"extra": "allow"}

    def __init__(self, trending_tools: TrendingTopics):
        super().__init__()
        self.trending_tools = trending_tools

    def _run(self, category: Optional[str] = None, keywords: Optional[str] = None, limit: int = 20) -> str:
        """执行热搜话题获取功能

        Args:
            category: 可选的分类名称，例如"科技"、"娱乐"、"教育"等
            keywords: 可选的关键词，用于过滤话题
            limit: 返回的话题数量上限，默认为20

        Returns:
            str: 包含热搜话题列表的文本
        """
        return self.trending_tools.execute(category=category, keywords=keywords, limit=limit)


class GetTopicDetailsTool(BaseTool):
    """话题详情获取工具"""
    name: str = "话题详情获取工具"
    description: str = "获取特定热搜话题的详细信息。"
    args_schema: Type[BaseModel] = TopicDetailsInput

    # 允许额外属性
    model_config = {"extra": "allow"}

    def __init__(self, trending_tools: TrendingTopics):
        super().__init__()
        self.trending_tools = trending_tools

    def _run(self, topic_id: str) -> str:
        """获取特定热搜话题的详细信息。

        Args:
            topic_id: 话题ID或话题完整名称

        Returns:
            str: 包含话题详细信息的文本
        """
        return self.trending_tools.execute(action="details", topic_id=topic_id)


class RecommendTopicsTool(BaseTool):
    """话题推荐工具"""
    name: str = "话题推荐工具"
    description: str = "基于目标受众和内容类型推荐合适的热搜话题。"
    args_schema: Type[BaseModel] = RecommendTopicsInput

    # 允许额外属性
    model_config = {"extra": "allow"}

    def __init__(self, trending_tools: TrendingTopics):
        super().__init__()
        self.trending_tools = trending_tools

    def _run(self, target_audience: Optional[str] = None, content_type: Optional[str] = None, limit: int = 5) -> str:
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

        # 创建工具实例
        self.get_trending_topics = GetTrendingTopicsTool(self.trending_tools)
        self.get_topic_details = GetTopicDetailsTool(self.trending_tools)
        self.recommend_topics = RecommendTopicsTool(self.trending_tools)
