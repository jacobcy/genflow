"""
选题团队工具测试

测试选题团队的所有工具能否被CrewAI正常使用，确保工具的基本可用性。
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# 导入选题团队工具
from core.agents.topic_crew.topic_tools import TopicTools

# 测试方便的装饰器，跳过对外部服务的实际调用
def mock_external_services(func):
    """装饰器，模拟外部服务调用"""
    patches = [
        patch("core.tools.trending_tools.TrendingTopics.execute",
              return_value=MagicMock(success=True, data="模拟热搜结果"))
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
async def test_get_trending_topics_with_crewai():
    """测试热搜话题获取工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = TopicTools()

    # 创建Agent和Task
    agent = Agent(
        role="Topic Agent",
        goal="测试热搜话题获取工具",
        backstory="我是测试热搜话题获取工具的Agent",
        tools=[tools.get_trending_topics]
    )

    task = Task(
        description="获取当前热搜话题",
        expected_output="热搜话题列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)
    assert hasattr(agent.tools[0], "_run")

@mock_external_services
async def test_get_topic_details_with_crewai():
    """测试话题详情获取工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = TopicTools()

    # 创建Agent和Task
    agent = Agent(
        role="Topic Agent",
        goal="测试话题详情获取工具",
        backstory="我是测试话题详情获取工具的Agent",
        tools=[tools.get_topic_details]
    )

    task = Task(
        description="获取特定话题的详细信息",
        expected_output="话题详情",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)
    assert hasattr(agent.tools[0], "_run")

@mock_external_services
async def test_recommend_topics_with_crewai():
    """测试话题推荐工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = TopicTools()

    # 创建Agent和Task
    agent = Agent(
        role="Topic Agent",
        goal="测试话题推荐工具",
        backstory="我是测试话题推荐工具的Agent",
        tools=[tools.recommend_topics]
    )

    task = Task(
        description="推荐合适的话题",
        expected_output="推荐话题列表",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert isinstance(agent.tools[0], BaseTool)
    assert hasattr(agent.tools[0], "_run")

@mock_external_services
async def test_all_topic_tools_with_crewai():
    """测试所有选题团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = TopicTools()

    # 获取所有工具方法
    all_tools = [
        tools.get_trending_topics,
        tools.get_topic_details,
        tools.recommend_topics
    ]

    # 创建Agent和Task
    agent = Agent(
        role="Topic Agent",
        goal="测试所有选题工具",
        backstory="我是测试所有选题工具的Agent",
        tools=all_tools
    )

    task = Task(
        description="使用各种选题工具发现和分析热门话题",
        expected_output="话题分析结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == len(all_tools)
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
