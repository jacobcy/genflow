"""
模拟工具模块

提供测试所需的模拟类，确保测试可以在没有完整依赖时运行。
"""
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 如果导入失败，使用模拟版本
try:
    from core.tools.base import ToolResult, BaseTool
    logger.info("成功导入工具基类")
except ImportError:
    logger.warning("导入工具基类失败，使用模拟版本")

    @dataclass
    class ToolResult:
        """工具执行结果（模拟版本）"""
        success: bool
        data: Any
        error: Optional[str] = None
        metadata: Optional[Dict] = None

    class BaseTool:
        """工具基类（模拟版本）"""
        name: str = "mock_tool"
        description: str = "模拟工具"

        def __init__(self, config: Dict = None):
            self.config = config or {}
            logger.info(f"初始化模拟工具: {self.name}")

        async def execute(self, *args, **kwargs) -> ToolResult:
            """执行工具功能"""
            logger.info(f"执行模拟工具: {self.name}")
            return ToolResult(success=True, data="模拟数据", metadata={"mock": True})

        def get_description(self) -> Dict:
            """获取工具描述"""
            return {
                "name": self.name,
                "description": self.description,
                "config": self.config
            }

# 模拟聚合工具类
class MockAggregator(BaseTool):
    """模拟聚合工具基类"""
    name = "mock_aggregator"
    description = "模拟聚合工具"

    def __init__(self, config: Dict = None):
        super().__init__(config)

    async def execute(self, *args, **kwargs) -> ToolResult:
        """模拟执行"""
        logger.info(f"执行模拟聚合工具: {kwargs}")
        return ToolResult(
            success=True,
            data="模拟聚合结果",
            metadata={"args": args, "kwargs": str(kwargs)}
        )

# 创建模拟版工具类，用于替代实际工具
class SearchAggregator(MockAggregator):
    """搜索聚合工具（模拟版本）"""
    name = "search_aggregator"
    description = "搜索聚合工具"

class ContentCollector(MockAggregator):
    """内容收集工具（模拟版本）"""
    name = "content_collector"
    description = "内容收集工具"

class NLPAggregator(MockAggregator):
    """NLP聚合工具（模拟版本）"""
    name = "nlp_aggregator"
    description = "NLP聚合工具"

class TrendingTopics(MockAggregator):
    """趋势话题工具（模拟版本）"""
    name = "trending_topics"
    description = "趋势话题工具"
