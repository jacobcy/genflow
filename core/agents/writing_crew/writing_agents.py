"""写作团队智能体"""
from typing import List, Dict
from crewai import Agent
from core.tools.nlp_tools import NLPAggregator, SummaTool, YakeTool
from core.tools.style_tools import StyleAdapter
from core.tools.writing_tools import ArticleWriter
from core.models.platform import Platform

class WritingAgents:
    """写作团队智能体定义"""

    def __init__(self, platform: Platform):
        """初始化工具

        Args:
            platform: 目标平台
        """
        self.platform = platform
        self.nlp_tools = NLPAggregator()
        self.summa_tool = SummaTool()
        self.yake_tool = YakeTool()
        self.style_adapter = StyleAdapter.get_instance(platform)
        self.article_writer = ArticleWriter()

    def create_outline_writer(self) -> Agent:
        """创建大纲撰写员"""
        return Agent(
            role='大纲撰写员',
            goal='设计清晰的文章结构',
            backstory="""你是一位专业的大纲撰写员，擅长设计文章的整体结构和逻辑框架。
            你需要根据研究报告设计出引人入胜且逻辑严密的文章大纲。""",
            tools=[
                self.article_writer.execute,
                self.nlp_tools.execute,
                self.yake_tool.execute
            ]
        )

    def create_content_writer(self) -> Agent:
        """创建内容撰写员"""
        return Agent(
            role='内容撰写员',
            goal='撰写高质量的文章内容',
            backstory="""你是一位资深的内容撰写员，擅长将研究成果转化为生动的文章。
            你需要根据大纲撰写出专业、易懂且有趣的内容。""",
            tools=[
                self.article_writer.execute,
                self.nlp_tools.execute,
                self.summa_tool.execute,
                self.style_adapter.execute
            ]
        )

    def create_seo_optimizer(self) -> Agent:
        """创建SEO优化师"""
        return Agent(
            role='SEO优化师',
            goal='优化文章的搜索引擎表现',
            backstory="""你是一位专业的SEO优化师，擅长提升文章的搜索引擎表现。
            你需要分析关键词、优化标题和内容结构，确保文章易于被搜索引擎发现。""",
            tools=[
                self.yake_tool.execute,
                self.nlp_tools.execute
            ]
        )

    def create_editor(self) -> Agent:
        """创建文章编辑"""
        return Agent(
            role='文章编辑',
            goal='提升文章的整体质量',
            backstory="""你是一位经验丰富的文章编辑，擅长优化文章的表达和结构。
            你需要确保文章的专业性、可读性和吸引力。""",
            tools=[
                self.nlp_tools.execute,
                self.summa_tool.execute,
                self.style_adapter.execute
            ]
        )
