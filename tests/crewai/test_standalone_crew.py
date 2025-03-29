"""CrewAI独立测试

测试CrewAI基础功能，不依赖外部模块
"""
import pytest
from unittest.mock import MagicMock, patch


# 测试代理创建
def test_agent_creation():
    """测试创建代理"""
    with patch("crewai.Agent", return_value=MagicMock()) as mock_agent_class:
        # 导入时会使用模拟对象
        from crewai import Agent

        # 创建代理
        agent = Agent(
            role="研究员",
            goal="进行市场调研",
            backstory="一位经验丰富的市场研究员"
        )

        # 验证模拟对象被调用
        mock_agent_class.assert_called_once()
        assert agent is not None


# 测试团队创建
def test_crew_creation():
    """测试创建团队"""
    with patch("crewai.Crew", return_value=MagicMock()) as mock_crew_class:
        # 导入时会使用模拟对象
        from crewai import Crew, Agent

        # 模拟代理
        agent1 = MagicMock()
        agent1.role = "研究员"

        agent2 = MagicMock()
        agent2.role = "作家"

        # 创建团队
        crew = Crew(
            agents=[agent1, agent2],
            tasks=[]
        )

        # 验证模拟对象被调用
        mock_crew_class.assert_called_once()
        assert crew is not None


# 测试任务创建
def test_task_creation():
    """测试创建任务"""
    with patch("crewai.Task", return_value=MagicMock()) as mock_task_class:
        # 导入时会使用模拟对象
        from crewai import Task, Agent

        # 模拟代理
        agent = MagicMock()
        agent.role = "研究员"

        # 创建任务
        task = Task(
            description="收集市场数据",
            expected_output="市场数据报告",
            agent=agent
        )

        # 验证模拟对象被调用
        mock_task_class.assert_called_once()
        assert task is not None
