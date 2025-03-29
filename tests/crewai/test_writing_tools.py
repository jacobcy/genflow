"""
写作团队工具测试

测试写作团队的所有工具能否被CrewAI正常使用，确保工具的基本可用性。
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool

# 导入写作团队工具
from core.agents.writing_crew.writing_tools import WritingTools

# 测试方便的装饰器，跳过对外部服务的实际调用
def mock_external_services(func):
    """装饰器，模拟外部服务调用"""
    patches = [
        patch("core.tools.nlp_tools.NLPAggregator.execute",
              return_value=MagicMock(success=True, data={"structure": "模拟结构分析"})),
        patch("core.tools.nlp_tools.SummaTool.execute",
              return_value=MagicMock(success=True, data="模拟内容摘要")),
        patch("core.tools.nlp_tools.YakeTool.execute",
              return_value=MagicMock(success=True, data=["关键词1", "关键词2"])),
        patch("core.tools.style_tools.adapter.StyleAdapter.adapt_article",
              return_value=MagicMock(return_value="模拟风格适配结果")),
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

@mock_external_services
async def test_analyze_structure_with_crewai():
    """测试文章结构分析工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试文章结构分析工具",
        backstory="我是测试文章结构分析工具的Agent",
        tools=[tools.analyze_structure]
    )

    task = Task(
        description="分析文章结构",
        expected_output="结构分析结果",
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
async def test_extract_keywords_with_crewai():
    """测试关键词提取工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试关键词提取工具",
        backstory="我是测试关键词提取工具的Agent",
        tools=[tools.extract_keywords]
    )

    task = Task(
        description="从文本中提取关键词",
        expected_output="关键词列表",
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
async def test_summarize_content_with_crewai():
    """测试内容摘要工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试内容摘要工具",
        backstory="我是测试内容摘要工具的Agent",
        tools=[tools.summarize_content]
    )

    task = Task(
        description="生成文本摘要",
        expected_output="文本摘要",
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
async def test_write_article_with_crewai():
    """测试文章撰写工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试文章撰写工具",
        backstory="我是测试文章撰写工具的Agent",
        tools=[tools.write_article]
    )

    task = Task(
        description="撰写一篇文章",
        expected_output="完成的文章",
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
async def test_adapt_style_with_crewai():
    """测试风格适配工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试风格适配工具",
        backstory="我是测试风格适配工具的Agent",
        tools=[tools.adapt_style]
    )

    task = Task(
        description="调整文本风格",
        expected_output="风格调整后的文本",
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
async def test_edit_article_with_crewai():
    """测试文章编辑工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试文章编辑工具",
        backstory="我是测试文章编辑工具的Agent",
        tools=[tools.edit_article]
    )

    task = Task(
        description="编辑和改进文章内容",
        expected_output="编辑后的文章",
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
async def test_all_writing_tools_with_crewai():
    """测试所有写作工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = WritingTools()

    # 创建Agent和Task
    agent = Agent(
        role="Writing Agent",
        goal="测试所有写作工具",
        backstory="我是测试所有写作工具的Agent",
        tools=[
            tools.analyze_structure,
            tools.extract_keywords,
            tools.summarize_content,
            tools.write_article,
            tools.adapt_style,
            tools.edit_article
        ]
    )

    task = Task(
        description="测试所有写作工具",
        expected_output="测试结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 6
    for tool in agent.tools:
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, "_run")

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
