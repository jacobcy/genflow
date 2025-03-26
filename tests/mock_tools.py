"""
模拟工具模块 - CrewAI新版兼容

提供测试所需的模拟类，确保测试可以在没有完整依赖时运行。
"""
from typing import Any, Dict, Optional, List
import logging
from crewai.tools import BaseTool

# 配置日志
logger = logging.getLogger(__name__)

class MockTool(BaseTool):
    """CrewAI兼容的模拟工具基类"""
    name: str = "mock_tool"
    description: str = "模拟工具"

    def __init__(self, config: Dict = None):
        super().__init__()
        self.config = config or {}
        logger.info(f"初始化模拟工具: {self.name}")

    def _run(self, *args, **kwargs) -> str:
        """执行工具功能 - 符合新版CrewAI要求"""
        logger.info(f"执行模拟工具: {self.name}")
        return "模拟数据"

# 模拟聚合工具类
class MockAggregator(MockTool):
    """模拟聚合工具基类"""
    name = "mock_aggregator"
    description = "模拟聚合工具"

    def _run(self, **kwargs) -> str:
        """模拟执行"""
        logger.info(f"执行模拟聚合工具: {kwargs}")
        return "模拟聚合结果"

# 创建模拟版工具类
class SearchAggregator(MockAggregator):
    """搜索聚合工具"""
    name = "search_aggregator"
    description = "搜索聚合工具"

class ContentCollector(MockAggregator):
    """内容收集工具"""
    name = "content_collector"
    description = "内容收集工具"

class NLPAggregator(MockAggregator):
    """NLP聚合工具"""
    name = "nlp_aggregator"
    description = "NLP聚合工具"

class TrendingTopics(MockAggregator):
    """趋势话题工具"""
    name = "trending_topics"
    description = "趋势话题工具"
