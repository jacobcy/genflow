"""
CrewAI工具测试

测试各个团队的工具能否被CrewAI正常使用，确保工具的基本可用性。
这些测试专注于验证工具是否能被CrewAI正确调用，而不测试具体实现。
"""

import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# 导入要测试的工具类
from core.agents.research_crew.research_tools import ResearchTools
from core.agents.review_crew.review_tools import ReviewTools
from core.agents.topic_crew.topic_tools import TopicTools
from core.agents.writing_crew.writing_tools import WritingTools
from core.models.platform import Platform

# 测试方便的装饰器，跳过对外部服务的实际调用
def mock_external_services(func):
    """装饰器，模拟外部服务调用"""
    patches = [
        patch("core.tools.content_collectors.ContentCollector.execute",
              return_value=MagicMock(success=True, data="模拟内容收集结果")),
        patch("core.tools.search_tools.SearchAggregator.execute",
              return_value=MagicMock(success=True, data="模拟搜索结果")),
        patch("core.tools.nlp_tools.NLPAggregator.execute",
              return_value=MagicMock(success=True, data="模拟NLP结果")),
        patch("core.tools.trending_tools.TrendingTopics.execute",
              return_value=MagicMock(success=True, data="模拟热搜结果")),
        patch("core.tools.review_tools.reviewer.PlagiarismChecker.execute",
              return_value=MagicMock(success=True, data={"plagiarism_rate": 0.1})),
        patch("core.tools.review_tools.reviewer.SensitiveWordChecker.execute",
              return_value=MagicMock(success=True, data={"sensitive_words": []})),
        patch("core.tools.style_tools.adapter.StyleAdapter.adapt_article",
              return_value=MagicMock(success=True, data="模拟风格适配结果")),
        patch("core.tools.writing_tools.article_writer.ArticleWriter.generate_article",
              return_value=MagicMock(success=True, data="模拟文章写作结果")),
        # 模拟 ArticleWriter 类，避免实例化
        patch("core.agents.writing_crew.writing_tools.ArticleWriter", return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(success=True, data="模拟文章写作结果"))
        ))
    ]

    @pytest.mark.asyncio
    async def wrapper(*args, **kwargs):
        for p in patches:
            p.start()
        try:
            await func(*args, **kwargs)
        finally:
            for p in patches:
                p.stop()

    return wrapper

# 测试研究团队工具
@mock_external_services
async def test_research_tools_with_crewai():
    """测试研究团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试研究工具",
        backstory="我是测试研究工具的Agent",
        tools=[tools.collect_content, tools.search_expert_opinions, tools.analyze_data]
    )

    task = Task(
        description="使用研究工具收集有关'人工智能'的信息",
        expected_output="收集到的研究信息",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 不实际执行kickoff，而是验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 3
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

# 测试审核团队工具
@mock_external_services
async def test_review_tools_with_crewai():
    """测试审核团队工具能否被CrewAI正常使用"""
    # 创建默认平台
    platform = Platform(name="测试平台", url="https://test.com")

    # 初始化工具
    tools = ReviewTools(platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试审核工具",
        backstory="我是测试审核工具的Agent",
        tools=[tools.check_plagiarism, tools.check_sensitive_content, tools.analyze_content_quality]
    )

    task = Task(
        description="审核一篇关于'技术发展'的文章",
        expected_output="审核结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 3
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

# 测试选题团队工具
@mock_external_services
async def test_topic_tools_with_crewai():
    """测试选题团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = TopicTools()

    # 创建Agent和Task
    agent = Agent(
        role="Topic Agent",
        goal="测试选题工具",
        backstory="我是测试选题工具的Agent",
        tools=[tools.get_trending_topics, tools.get_topic_details, tools.recommend_topics]
    )

    task = Task(
        description="发现热门技术话题",
        expected_output="热门话题列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 3
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

# 测试写作团队工具
@mock_external_services
async def test_writing_tools_with_crewai():
    """测试写作团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试写作工具",
        backstory="我是测试写作工具的Agent",
        tools=[tools.analyze_structure, tools.extract_keywords, tools.write_article]
    )

    task = Task(
        description="写一篇关于'AI发展'的文章",
        expected_output="完成的文章",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 3
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
