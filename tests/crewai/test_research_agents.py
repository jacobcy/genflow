"""
研究团队智能体测试

测试研究团队智能体的核心功能，包括单例模式、智能体创建和工具绑定。
"""

import pytest
from unittest.mock import patch, MagicMock
from crewai import Agent
from crewai.tools import BaseTool

from core.agents.research_crew.research_agents import ResearchAgents
from core.config import Config
from tests.mock_tools import MockTool

# 清理单例，确保测试隔离
@pytest.fixture(autouse=True)
def clear_instance():
    """每个测试前清理单例实例"""
    ResearchAgents.clear_instance()
    yield
    ResearchAgents.clear_instance()

def test_get_instance_singleton():
    """测试ResearchAgents的单例模式"""
    # 获取第一个实例
    instance1 = ResearchAgents.get_instance()
    # 获取第二个实例
    instance2 = ResearchAgents.get_instance()

    # 验证两个实例是同一个对象
    assert instance1 is instance2

    # 清除实例后，应创建新实例
    ResearchAgents.clear_instance()
    instance3 = ResearchAgents.get_instance()

    # 验证清除后创建的是新实例
    assert instance1 is not instance3

def test_config_propagation():
    """测试配置对象是否正确传递"""
    with patch("core.agents.research_crew.research_agents.ResearchTools") as mock_tools:
        # 创建自定义配置
        custom_config = Config()

        # 初始化带有自定义配置的智能体管理器
        agent_manager = ResearchAgents(config=custom_config)

        # 验证配置是否正确传递给ResearchTools
        mock_tools.assert_called_once_with(config=custom_config)

        # 验证配置是否存储在agent_manager中
        assert agent_manager.config is custom_config

def test_create_all_agents():
    """测试创建所有智能体"""
    # 创建模拟工具类实例
    with patch("core.agents.research_crew.research_agents.ResearchTools") as mock_tools_class:
        # 创建一个真实的Mock工具集实例
        mock_tools_instance = MagicMock()

        # 为每个工具方法创建MockTool实例
        tool_methods = [
            "collect_content", "search_expert_opinions", "analyze_data",
            "generate_research_report", "extract_key_findings",
            "validate_facts", "search_related_resources",
            "compare_perspectives", "analyze_statistics"
        ]

        for method in tool_methods:
            # 设置工具方法为MockTool实例
            mock_tool = MockTool()
            mock_tool.name = method
            mock_tool.description = f"Mock {method} tool"
            setattr(mock_tools_instance, method, mock_tool)

        # 设置模拟工具集返回值
        mock_tools_class.return_value = mock_tools_instance

        # 在真实的Agent初始化前创建补丁
        with patch("core.agents.research_crew.research_agents.Agent") as mock_agent:
            # 确保Agent构造函数返回一个MagicMock
            mock_agent_instance = MagicMock()
            mock_agent.return_value = mock_agent_instance

            # 初始化智能体管理器
            agent_manager = ResearchAgents()

            # 创建所有智能体
            agents = agent_manager.create_all_agents()

            # 验证返回了所有四种智能体
            assert len(agents) == 4
            assert "background_researcher" in agents
            assert "expert_finder" in agents
            assert "data_analyst" in agents
            assert "research_writer" in agents

            # 验证Agent类被正确调用了4次
            assert mock_agent.call_count == 4

def test_tools_assigned_to_agents():
    """测试工具正确分配给智能体"""
    # 创建模拟工具类实例
    with patch("core.agents.research_crew.research_agents.ResearchTools") as mock_tools_class:
        # 创建一个真实的Mock工具集实例
        mock_tools_instance = MagicMock()

        # 为每个工具方法创建MockTool实例
        tool_methods = [
            "collect_content", "search_expert_opinions", "analyze_data",
            "generate_research_report", "extract_key_findings",
            "validate_facts", "search_related_resources",
            "compare_perspectives", "analyze_statistics"
        ]

        for method in tool_methods:
            # 设置工具方法为MockTool实例
            mock_tool = MockTool()
            mock_tool.name = method
            mock_tool.description = f"Mock {method} tool"
            setattr(mock_tools_instance, method, mock_tool)

        # 设置模拟工具集返回值
        mock_tools_class.return_value = mock_tools_instance

        # 跟踪工具分配
        tools_assigned = {
            "background_researcher": [],
            "expert_finder": [],
            "data_analyst": [],
            "research_writer": []
        }

        # 模拟Agent初始化，捕获传递给它的工具
        def mock_agent_init(role, goal, backstory, tools, verbose, allow_delegation):
            # 根据角色名称存储工具
            role_name = role
            if role == "背景研究员":
                tools_assigned["background_researcher"] = tools
            elif role == "专家发现者":
                tools_assigned["expert_finder"] = tools
            elif role == "数据分析师":
                tools_assigned["data_analyst"] = tools
            elif role == "研究报告撰写员":
                tools_assigned["research_writer"] = tools
            return MagicMock()

        # 在真实的Agent初始化前创建补丁
        with patch("core.agents.research_crew.research_agents.Agent") as mock_agent:
            # 设置模拟实现
            mock_agent.side_effect = mock_agent_init

            # 初始化智能体管理器
            agent_manager = ResearchAgents()

            # 创建所有智能体
            agent_manager.create_all_agents()

            # 验证每个智能体都被分配了正确数量的工具
            assert len(tools_assigned["background_researcher"]) == 4
            assert len(tools_assigned["expert_finder"]) == 4
            assert len(tools_assigned["data_analyst"]) == 4
            assert len(tools_assigned["research_writer"]) == 3

            # 验证工具都是BaseTool的实例
            for role, tools in tools_assigned.items():
                for tool in tools:
                    assert isinstance(tool, BaseTool)

def test_individual_agent_creation():
    """测试单独创建各个智能体"""
    # 创建模拟工具类实例
    with patch("core.agents.research_crew.research_agents.ResearchTools") as mock_tools_class:
        # 创建一个真实的Mock工具集实例
        mock_tools_instance = MagicMock()

        # 为每个工具方法创建MockTool实例
        tool_methods = [
            "collect_content", "search_expert_opinions", "analyze_data",
            "generate_research_report", "extract_key_findings",
            "validate_facts", "search_related_resources",
            "compare_perspectives", "analyze_statistics"
        ]

        for method in tool_methods:
            # 设置工具方法为MockTool实例
            mock_tool = MockTool()
            mock_tool.name = method
            mock_tool.description = f"Mock {method} tool"
            setattr(mock_tools_instance, method, mock_tool)

        # 设置模拟工具集返回值
        mock_tools_class.return_value = mock_tools_instance

        # 模拟Agent
        with patch("core.agents.research_crew.research_agents.Agent") as mock_agent:
            # 设置Agent返回值
            mock_agent.return_value = MagicMock()

            # 初始化智能体管理器
            agent_manager = ResearchAgents()

            # 测试每个创建方法，检查是否调用了Agent构造函数
            agent_manager.create_background_researcher()
            assert mock_agent.call_count == 1

            agent_manager.create_expert_finder()
            assert mock_agent.call_count == 2

            agent_manager.create_data_analyst()
            assert mock_agent.call_count == 3

            agent_manager.create_research_writer()
            assert mock_agent.call_count == 4

if __name__ == "__main__":
    # 执行所有测试
    pytest.main(["-xvs", __file__])
