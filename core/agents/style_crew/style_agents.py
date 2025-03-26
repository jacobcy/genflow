"""风格化团队的智能体定义

该模块定义了风格化团队中使用的各个智能体，包括平台分析师、风格专家、内容适配器和质量检查员。
"""

import logging
from typing import Dict, List, Optional, Any

from crewai import Agent
from core.tools.style_tools.adapter import StyleAdapter
from core.constants.style_types import get_style_features, get_style_description

logger = logging.getLogger(__name__)

class PlatformAnalystAgent:
    """平台分析师智能体

    负责分析平台特点和风格规范，为后续风格化提供基础。
    """

    def __init__(self, style_adapter: StyleAdapter):
        """初始化平台分析师智能体

        Args:
            style_adapter: 风格适配器
        """
        self.style_adapter = style_adapter
        self.agent = None

    def get_agent(self) -> Agent:
        """获取智能体实例

        Returns:
            Agent: CrewAI智能体实例
        """
        if self.agent is None:
            self.agent = Agent(
                role="平台风格分析师",
                goal="深入分析内容平台的风格特点和规范要求",
                backstory="""你是一位专业的平台内容分析师，对各大内容平台的风格、调性、用户偏好有深入研究。
                你能够快速识别平台的核心风格特点，并提供详细的分析报告。
                你将优先使用我们的style_types模块提供的预定义风格信息，如果可用的话。""",
                verbose=True,
                allow_delegation=False,
                # 工具可以根据实际情况添加
                tools=[self.style_adapter.execute]
            )
        return self.agent


class StyleExpertAgent:
    """风格专家智能体

    负责根据平台特点和原始内容，制定风格改写策略。
    """

    def __init__(self, style_adapter: StyleAdapter):
        """初始化风格专家智能体

        Args:
            style_adapter: 风格适配器
        """
        self.style_adapter = style_adapter
        self.agent = None

    def get_agent(self) -> Agent:
        """获取智能体实例

        Returns:
            Agent: CrewAI智能体实例
        """
        if self.agent is None:
            self.agent = Agent(
                role="内容风格专家",
                goal="为内容提供最适合目标平台的风格改写建议",
                backstory="""你是一位资深的内容风格顾问，精通各类写作风格和表达方式。
                你能够根据平台特点和原始内容，提供精准的风格调整建议，确保内容在目标平台上获得最佳效果。
                你会使用style_types模块提供的预定义风格，包括各平台的特有表达方式、语调和形式。""",
                verbose=True,
                allow_delegation=False,
                tools=[self.style_adapter.execute]
            )
        return self.agent


class ContentAdapterAgent:
    """内容适配器智能体

    负责根据风格建议对内容进行实际改写。
    """

    def __init__(self, style_adapter: StyleAdapter):
        """初始化内容适配器智能体

        Args:
            style_adapter: 风格适配器
        """
        self.style_adapter = style_adapter
        self.agent = None

    def get_agent(self) -> Agent:
        """获取智能体实例

        Returns:
            Agent: CrewAI智能体实例
        """
        if self.agent is None:
            self.agent = Agent(
                role="内容改写专家",
                goal="按照风格建议对内容进行高质量改写，保持原意的同时调整风格",
                backstory="""你是一位创意写作高手，擅长在保持原始内容核心信息的同时，
                调整语言风格、叙述方式和表达结构，使内容更符合目标平台的风格要求。
                你将使用从风格专家那里获得的建议，结合style_types模块提供的预定义风格规范。""",
                verbose=True,
                allow_delegation=False,
                tools=[self.style_adapter.execute]
            )
        return self.agent


class QualityCheckerAgent:
    """质量检查员智能体

    负责检查改写后内容的质量和合规性。
    """

    def __init__(self, style_adapter: StyleAdapter):
        """初始化质量检查员智能体

        Args:
            style_adapter: 风格适配器
        """
        self.style_adapter = style_adapter
        self.agent = None

    def get_agent(self) -> Agent:
        """获取智能体实例

        Returns:
            Agent: CrewAI智能体实例
        """
        if self.agent is None:
            self.agent = Agent(
                role="内容质量检查员",
                goal="确保风格化后的内容符合平台规范并保持高质量",
                backstory="""你是一位严谨的内容质量控制专家，对内容质量标准和平台规范有深入了解。
                你会仔细审查改写后的内容，确保其符合平台风格要求，同时保持内容质量和准确性。
                你可以通过style_types模块获取平台规范，确保内容与预定义的风格标准一致。""",
                verbose=True,
                allow_delegation=False,
                tools=[self.style_adapter.execute]
            )
        return self.agent
