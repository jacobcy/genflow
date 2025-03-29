"""
CrewAI测试的配置文件

提供CrewAI测试所需的夹具和模拟对象
"""
import pytest
from unittest.mock import MagicMock, patch

# CrewAI测试特定的夹具

@pytest.fixture(scope="function")
def mock_llm():
    """提供模拟的LLM对象"""
    mock_llm = MagicMock()
    mock_llm.generate.return_value = MagicMock()
    mock_llm.generate.return_value.generations = [[MagicMock(text="模拟的LLM响应")]]
    return mock_llm

@pytest.fixture(scope="function")
def mock_agent():
    """提供模拟的Agent对象"""
    mock_agent = MagicMock()
    mock_agent.run.return_value = "模拟的代理执行结果"
    return mock_agent

@pytest.fixture(scope="function")
def mock_research_tools():
    """提供模拟的ResearchTools对象"""
    mock_tools = MagicMock()
    mock_tools.search_web.return_value = "模拟的网络搜索结果"
    mock_tools.summarize_text.return_value = "模拟的文本摘要"
    mock_tools.collect_data.return_value = "模拟的数据收集结果"
    mock_tools.analyze_data.return_value = "模拟的数据分析结果"
    return mock_tools

@pytest.fixture(scope="function")
def mock_content_collector():
    """提供模拟的ContentCollector对象"""
    mock_collector = MagicMock()
    mock_collector.collect.return_value = "模拟的内容收集结果"
    return mock_collector

@pytest.fixture(scope="function")
def mock_crew():
    """提供模拟的Crew对象"""
    mock_crew = MagicMock()
    mock_crew.kickoff.return_value = "模拟的团队执行结果"
    return mock_crew

@pytest.fixture(scope="function")
def mock_task():
    """提供模拟的Task对象"""
    mock_task = MagicMock()
    mock_task.execute.return_value = "模拟的任务执行结果"
    return mock_task

@pytest.fixture(scope="function")
def mock_topic_tools():
    """提供模拟的TopicTools对象"""
    mock_tools = MagicMock()
    mock_tools.generate_topic.return_value = "模拟的话题生成结果"
    mock_tools.analyze_topic.return_value = "模拟的话题分析结果"
    return mock_tools

@pytest.fixture(scope="function")
def mock_writing_tools():
    """提供模拟的WritingTools对象"""
    mock_tools = MagicMock()
    mock_tools.generate_outline.return_value = "模拟的大纲生成结果"
    mock_tools.write_section.return_value = "模拟的章节写作结果"
    return mock_tools

@pytest.fixture(scope="function")
def mock_review_tools():
    """提供模拟的ReviewTools对象"""
    mock_tools = MagicMock()
    mock_tools.review_content.return_value = "模拟的内容审查结果"
    mock_tools.check_quality.return_value = "模拟的质量检查结果"
    return mock_tools
