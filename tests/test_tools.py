"""工具测试模块"""
import pytest
import asyncio
import logging
from typing import Optional, Dict, Any, Type

# 配置日志记录器
logger = logging.getLogger(__name__)

# 导入基础类
from src.tools.base import BaseTool, ToolResult

# 导入工具类
from src.tools.content_collectors import (
    ContentCollector,
    NewspaperCollector,
    TrafilaturaCollector,
    ReadabilityCollector
)
from src.tools.search_tools import SearchAggregator, DuckDuckGoTool, GoogleTrendsTool
from src.tools.nlp_tools import NLPAggregator
from src.tools.style_tools import StyleAdapter
from src.tools.trending_tools import TrendingTopics
from src.tools.review_tools import (
    PlagiarismChecker,
    StatisticalAIDetector,
    OpenAIDetector,
    SensitiveWordChecker
)
from src.agents.content_crew import ContentCrew
from src.models.platform import Platform, StyleRules, ContentRules, StyleGuide, SEORequirements

# 测试数据
TEST_URL = "https://www.python.org"
TEST_NEWS_URL = "https://www.bbc.com/news/articles/cjevg23enggo"
TEST_SEARCH_QUERY = "Python编程"
TEST_TEXT = """
Python是一种高级编程语言。Python的设计哲学
强调代码的可读性，它使用缩进来组织代码块。
Python是动态类型的，并且具有垃圾回收功能。
它支持多种编程范式，包括结构化、面向对象和
函数式编程。
"""

class BaseToolTest:
    """工具测试基类"""
    
    @pytest.fixture(autouse=True)
    async def setup_tool(self):
        """设置工具实例"""
        self.tool = self.get_tool_instance()
        yield
        if hasattr(self.tool, 'cleanup'):
            await self.tool.cleanup()
    
    def get_tool_instance(self) -> BaseTool:
        """获取工具实例，子类必须实现"""
        raise NotImplementedError
    
    async def verify_tool_result(self, result: ToolResult):
        """验证工具执行结果"""
        logger.info(f"验证工具执行结果: {result}")
        assert result is not None
        assert isinstance(result, ToolResult)
        assert result.success
        assert result.data is not None
        return result

@pytest.mark.asyncio
class TestContentTools(BaseToolTest):
    """内容采集工具测试"""
    
    def get_tool_instance(self) -> ContentCollector:
        return ContentCollector()
    
    async def test_content_collector(self):
        """测试内容采集聚合工具"""
        logger.info("开始测试内容采集器")
        # 测试新闻文章
        result = await self.verify_tool_result(
            await self.tool.execute(TEST_NEWS_URL)
        )
        assert "tool_used" in result.metadata
        
        # 测试普通网页
        await self.verify_tool_result(
            await self.tool.execute(TEST_URL)
        )
        logger.info("内容采集器测试完成")

@pytest.mark.asyncio
class TestSearchTools(BaseToolTest):
    """搜索工具测试"""
    
    def get_tool_instance(self) -> SearchAggregator:
        return SearchAggregator()
    
    async def test_search_aggregator(self):
        """测试搜索聚合工具"""
        logger.info("开始测试搜索聚合器")
        result = await self.verify_tool_result(
            await self.tool.execute(TEST_SEARCH_QUERY)
        )
        assert "duckduckgo" in result.data
        assert len(result.data["duckduckgo"]) > 0
        logger.info("搜索聚合器测试完成")

@pytest.mark.asyncio
class TestNLPTools(BaseToolTest):
    """NLP工具测试"""
    
    def get_tool_instance(self) -> NLPAggregator:
        return NLPAggregator()
    
    async def test_nlp_aggregator(self):
        """测试 NLP 聚合工具"""
        logger.info("开始测试NLP聚合器")
        result = await self.verify_tool_result(
            await self.tool.execute(TEST_TEXT)
        )
        # 检查各工具结果
        assert "Python" in result.data
        logger.info("NLP聚合器测试完成")

@pytest.mark.asyncio
class TestStyleTools(BaseToolTest):
    """样式工具测试"""
    
    def get_tool_instance(self) -> StyleAdapter:
        platform = Platform(
            id="wechat",
            name="WeChat",
            type="social",
            url="https://wechat.com",
            content_rules=ContentRules(),
            style_guide=StyleGuide(),
            seo_requirements=SEORequirements(),
            publish_settings={},
            style_rules=StyleRules(
                tone="professional",
                formality=3,
                emotion=False,
                code_block=False,
                emoji=False,
                image_text_ratio=0.3,
                max_image_count=10,
                min_paragraph_length=100,
                max_paragraph_length=500,
                paragraph_count_range=(5, 20),
                section_count_range=(3, 10),
                title_length_range=(10, 50),
                keyword_density=0.02,
                heading_required=True,
                tag_count_range=(3, 8)
            )
        )
        return StyleAdapter.get_instance(platform)
    
    async def test_style_adapter(self):
        """测试样式适配器基本功能"""
        logger.info("开始测试样式适配器")
        result = await self.verify_tool_result(
            await self.tool.execute(
                text="测试文本",
                platform="wechat"
            )
        )
        logger.info("样式适配器测试完成")

@pytest.mark.asyncio
class TestContentCrew:
    """内容生成团队测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_crew(self):
        """设置内容生成团队"""
        self.crew = ContentCrew()
        yield
        if hasattr(self.crew, 'cleanup'):
            await self.crew.cleanup()
    
    async def test_content_crew_initialization(self):
        """测试内容生成团队初始化"""
        logger.info("开始测试内容生成团队初始化")
        assert self.crew.researcher is not None
        assert self.crew.writer is not None
        assert self.crew.stylist is not None
        assert self.crew.reviewer is not None
        assert self.crew.editor is not None
        logger.info("内容生成团队初始化测试完成")
    
    async def test_content_creation(self):
        """测试内容生成流程"""
        logger.info("开始测试内容生成流程")
        result = await self.crew.create_content(
            topic="Python测试最佳实践",
            platform="zhihu"
        )
        assert isinstance(result, dict)
        assert "content" in result
        assert "metadata" in result
        assert result["metadata"]["status"] == "success"
        logger.info(f"内容生成完成，元数据: {result['metadata']}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("开始测试错误处理")
        with pytest.raises(RuntimeError) as exc_info:
            await self.crew.create_content(topic="", platform="invalid_platform")
        logger.info(f"错误处理测试完成，捕获到异常: {exc_info.value}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    pytest.main(["-v", "--log-cli-level=INFO"]) 