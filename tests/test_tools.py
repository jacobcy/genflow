"""工具测试模块"""
import pytest
import asyncio
import logging
from typing import Optional, Dict, Any, Type

# 配置日志记录器
logger = logging.getLogger(__name__)

# 导入基础类
from core.tools.base import BaseTool, ToolResult

# 导入工具类
from core.tools.content_collectors import (
    ContentCollector,
    NewspaperCollector,
    TrafilaturaCollector,
    ReadabilityCollector
)
from core.tools.search_tools import SearchAggregator, DuckDuckGoTool, GoogleTrendsTool
from core.tools.nlp_tools import NLPAggregator
from core.tools.style_tools import StyleAdapter
from core.tools.trending_tools import TrendingTopics
from core.tools.review_tools import (
    PlagiarismChecker,
    StatisticalAIDetector,
    OpenAIDetector,
    SensitiveWordChecker
)
from core.controllers.content_controller import ContentController
from core.models.platform import Platform, StyleRules, ContentRules, StyleGuide, SEORequirements
# 导入选题工具
from core.agents.topic_crew.topic_tools import TopicTools

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
class TestContentController:
    """内容生成团队测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_controller(self):
        """设置内容生成控制器"""
        self.controller = ContentController()
        yield
        if hasattr(self.controller, 'cleanup'):
            await self.controller.cleanup()
    
    async def test_content_controller_initialization(self):
        """测试内容生成控制器初始化"""
        logger.info("开始测试内容生成控制器初始化")
        assert self.controller.topic_crew is not None
        assert self.controller.research_crew is not None
        assert self.controller.writing_crew is not None
        assert self.controller.style_crew is not None
        assert self.controller.review_crew is not None
        logger.info("内容生成控制器初始化测试完成")
    
    async def test_content_creation(self):
        """测试内容生成流程"""
        logger.info("开始测试内容生成流程")
        result = await self.controller.produce_content(
            category="Python测试最佳实践",
            platform="zhihu",
            topic_count=1
        )
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "success"
        logger.info(f"内容生成完成，状态: {result['status']}")
    
    async def test_error_handling(self):
        """测试错误处理"""
        logger.info("开始测试错误处理")
        result = await self.controller.produce_content(
            category="",
            platform="invalid_platform"
        )
        assert result["status"] == "error"
        assert "error" in result
        logger.info(f"错误处理测试完成，捕获到错误: {result['error']}")

@pytest.mark.asyncio
class TestTopicTools:
    """选题工具测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_tool(self):
        """设置工具实例"""
        self.tool = TopicTools()
        yield
    
    async def test_tool_initialization(self):
        """测试工具初始化"""
        logger.info("开始测试选题工具初始化")
        # 验证核心工具实例是否正确初始化
        assert self.tool.search_tools is not None
        assert self.tool.content_collector is not None
        assert self.tool.nlp_tools is not None
        assert self.tool.trending_tools is not None
        logger.info("选题工具初始化测试完成")
    
    async def test_bound_methods(self):
        """测试方法绑定"""
        logger.info("开始测试工具方法绑定")
        # 验证所有工具方法都已正确绑定
        assert callable(self.tool.analyze_trends)
        assert callable(self.tool.fetch_trending_topics)
        assert callable(self.tool.search_web)
        assert callable(self.tool.search_professional)
        assert callable(self.tool.collect_content)
        assert callable(self.tool.collect_comments)
        assert callable(self.tool.analyze_text)
        assert callable(self.tool.analyze_topic_potential)
        assert callable(self.tool.analyze_competition)
        
        # 确认工具信息和装饰器属性已正确传递
        assert hasattr(self.tool.search_web, "_crewai_tool")
        
        logger.info("工具方法绑定测试完成")
    
    async def test_search_web_functionality(self):
        """测试网络搜索功能"""
        logger.info("开始测试网络搜索功能")
        # 模拟调用，不期望实际执行，只验证方法可调用
        # 我们会模拟search_tools.execute的返回，避免真实网络调用
        self.tool.search_tools.execute = lambda **kwargs: ToolResult(
            success=True,
            data="模拟搜索结果",
            metadata={"tool_used": "mock_search"}
        )
        
        try:
            # 测试方法是否可调用而不抛出绑定错误
            result = self.tool.search_web("测试查询")
            assert result is not None
            logger.info("网络搜索功能测试成功")
        except TypeError as e:
            if "missing required argument" in str(e):
                pytest.fail(f"方法绑定错误: {e}")
            else:
                pytest.fail(f"测试失败: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    pytest.main(["-v", "--log-cli-level=INFO"]) 