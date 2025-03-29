"""
研究团队工具测试

测试研究团队的所有工具能否被CrewAI正常使用，确保工具的基本可用性。
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# 导入研究团队工具
from core.agents.research_crew.research_tools import ResearchTools

# 测试方便的装饰器，跳过对外部服务的实际调用
def mock_external_services(func):
    """装饰器，模拟外部服务调用"""
    patches = [
        patch("core.tools.content_collectors.ContentCollector.execute",
              return_value=MagicMock(success=True, data="模拟内容收集结果")),
        patch("core.tools.search_tools.SearchAggregator.execute",
              return_value=MagicMock(success=True, data="模拟搜索结果")),
        patch("core.tools.nlp_tools.NLPAggregator.execute",
              return_value=MagicMock(success=True, data="模拟NLP结果"))
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

@mock_external_services
async def test_collect_content_with_crewai():
    """测试内容收集工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试内容收集工具",
        backstory="我是测试内容收集工具的Agent",
        tools=[tools.collect_content]
    )

    task = Task(
        description="收集关于'人工智能'的内容",
        expected_output="收集到的内容",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_search_expert_opinions_with_crewai():
    """测试专家观点搜索工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试专家观点搜索工具",
        backstory="我是测试专家观点搜索工具的Agent",
        tools=[tools.search_expert_opinions]
    )

    task = Task(
        description="寻找关于'气候变化'的专家观点",
        expected_output="专家观点列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_analyze_data_with_crewai():
    """测试数据分析工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试数据分析工具",
        backstory="我是测试数据分析工具的Agent",
        tools=[tools.analyze_data]
    )

    task = Task(
        description="分析文本数据并提取见解",
        expected_output="分析结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_generate_research_report_with_crewai():
    """测试研究报告生成工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试研究报告生成工具",
        backstory="我是测试研究报告生成工具的Agent",
        tools=[tools.generate_research_report]
    )

    task = Task(
        description="生成一份关于'技术趋势'的研究报告",
        expected_output="研究报告",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_extract_key_findings_with_crewai():
    """测试关键发现提取工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试关键发现提取工具",
        backstory="我是测试关键发现提取工具的Agent",
        tools=[tools.extract_key_findings]
    )

    task = Task(
        description="从长文本中提取关键发现",
        expected_output="关键发现列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_validate_facts_with_crewai():
    """测试事实验证工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试事实验证工具",
        backstory="我是测试事实验证工具的Agent",
        tools=[tools.validate_facts]
    )

    task = Task(
        description="验证关于'历史事件'的事实陈述",
        expected_output="验证结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_search_related_resources_with_crewai():
    """测试相关资源搜索工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试相关资源搜索工具",
        backstory="我是测试相关资源搜索工具的Agent",
        tools=[tools.search_related_resources]
    )

    task = Task(
        description="搜索与'神经网络'相关的资源",
        expected_output="资源列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_compare_perspectives_with_crewai():
    """测试观点对比分析工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试观点对比分析工具",
        backstory="我是测试观点对比分析工具的Agent",
        tools=[tools.compare_perspectives]
    )

    task = Task(
        description="对比分析关于'AI伦理'的不同观点",
        expected_output="观点对比分析",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_analyze_statistics_with_crewai():
    """测试定量统计分析工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试定量统计分析工具",
        backstory="我是测试定量统计分析工具的Agent",
        tools=[tools.analyze_statistics]
    )

    task = Task(
        description="分析文本中的统计数据",
        expected_output="统计分析结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)

@mock_external_services
async def test_all_research_tools_with_crewai():
    """测试所有研究团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ResearchTools()

    # 获取所有工具方法
    all_tools = [
        tools.collect_content,
        tools.search_expert_opinions,
        tools.analyze_data,
        tools.generate_research_report,
        tools.extract_key_findings,
        tools.validate_facts,
        tools.search_related_resources,
        tools.compare_perspectives,
        tools.analyze_statistics
    ]

    # 创建Agent和Task
    agent = Agent(
        role="Research Agent",
        goal="测试所有研究工具",
        backstory="我是测试所有研究工具的Agent",
        tools=all_tools
    )

    task = Task(
        description="使用各种研究工具完成综合研究",
        expected_output="研究结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == len(all_tools)
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
