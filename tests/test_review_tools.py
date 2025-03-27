"""
审核团队工具测试

测试审核团队的所有工具能否被CrewAI正常使用，确保工具的基本可用性。
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from crewai import Agent, Task, Crew
from functools import wraps

# 导入审核团队工具
from core.agents.review_crew.review_tools import ReviewTools
from core.models.platform import Platform

# 测试方便的装饰器，跳过对外部服务的实际调用
def mock_external_services(func):
    """装饰器，模拟外部服务调用"""
    patches = [
        patch("core.tools.nlp_tools.NLPAggregator.execute",
              return_value=MagicMock(success=True, data={"overall_score": 0.8})),
        patch("core.tools.review_tools.reviewer.PlagiarismChecker.execute",
              return_value=MagicMock(success=True, data={"plagiarism_rate": 0.1})),
        patch("core.tools.review_tools.reviewer.StatisticalAIDetector.execute",
              return_value=MagicMock(success=True, data={"ai_score": 0.3, "is_likely_ai": False})),
        patch("core.tools.review_tools.reviewer.OpenAIDetector.execute",
              return_value=MagicMock(success=True, data={"ai_score": 0.2, "is_likely_ai": False})),
        patch("core.tools.review_tools.reviewer.SensitiveWordChecker.execute",
              return_value=MagicMock(success=True, data={"sensitive_words": []}))
    ]

    @wraps(func)
    @pytest.mark.asyncio
    async def wrapper(*args, **kwargs):
        for p in patches:
            p.start()
        try:
            return await func(*args, **kwargs)
        finally:
            for p in patches:
                p.stop()

    return wrapper

# 创建测试用平台
@pytest.fixture
def test_platform():
    return Platform(
        name="测试平台",
        type="test",
        url="https://test.com",
        content_rules={
            "min_words": 500,
            "max_words": 5000,
            "allowed_tags": ["技术", "AI"],
            "sensitive_words": ["敏感词1", "敏感词2"]
        }
    )

@mock_external_services
async def test_check_plagiarism_with_crewai(test_platform):
    """测试原创性检测工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试原创性检测工具",
        backstory="我是测试原创性检测工具的Agent",
        tools=[tools.check_plagiarism]
    )

    task = Task(
        description="检测文章的原创性",
        expected_output="原创性检测结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_detect_ai_content_with_crewai(test_platform):
    """测试AI内容检测工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试AI内容检测工具",
        backstory="我是测试AI内容检测工具的Agent",
        tools=[tools.detect_ai_content]
    )

    task = Task(
        description="检测文章是否由AI生成",
        expected_output="AI检测结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_check_sensitive_content_with_crewai(test_platform):
    """测试敏感内容检测工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试敏感内容检测工具",
        backstory="我是测试敏感内容检测工具的Agent",
        tools=[tools.check_sensitive_content]
    )

    task = Task(
        description="检测文章中的敏感内容",
        expected_output="敏感内容检测结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_analyze_content_quality_with_crewai(test_platform):
    """测试内容质量分析工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试内容质量分析工具",
        backstory="我是测试内容质量分析工具的Agent",
        tools=[tools.analyze_content_quality]
    )

    task = Task(
        description="分析文章内容质量",
        expected_output="内容质量分析结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_evaluate_compliance_with_crewai(test_platform):
    """测试合规性评估工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试合规性评估工具",
        backstory="我是测试合规性评估工具的Agent",
        tools=[tools.evaluate_compliance]
    )

    task = Task(
        description="评估文章是否符合平台规范",
        expected_output="合规性评估结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_generate_review_report_with_crewai(test_platform):
    """测试审核报告生成工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试审核报告生成工具",
        backstory="我是测试审核报告生成工具的Agent",
        tools=[tools.generate_review_report]
    )

    task = Task(
        description="生成综合审核报告",
        expected_output="审核报告",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == 1
    assert callable(agent.tools[0])

@mock_external_services
async def test_all_review_tools_with_crewai(test_platform):
    """测试所有审核团队工具能否被CrewAI正常使用"""
    # 初始化工具
    tools = ReviewTools(test_platform)

    # 获取所有工具方法
    all_tools = [
        tools.check_plagiarism,
        tools.detect_ai_content,
        tools.check_sensitive_content,
        tools.analyze_content_quality,
        tools.evaluate_compliance,
        tools.generate_review_report
    ]

    # 创建Agent和Task
    agent = Agent(
        role="Review Agent",
        goal="测试所有审核工具",
        backstory="我是测试所有审核工具的Agent",
        tools=all_tools
    )

    task = Task(
        description="对文章进行全面审核",
        expected_output="审核结果",
        agent=agent
    )

    # 创建Crew（禁用实际执行）
    crew = Crew(agents=[agent], tasks=[task])

    # 验证工具是否被正确设置
    assert hasattr(agent, "tools")
    assert len(agent.tools) == len(all_tools)
    for tool in agent.tools:
        assert callable(tool)

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
