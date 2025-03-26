"""研究团队智能体

这个模块定义了研究团队的智能体角色，每个智能体负责特定的研究任务领域。
研究团队专注于深入研究选定话题，收集和分析相关信息，生成结构化的研究报告。
"""
from typing import List, Dict, Optional, Any, ClassVar
import logging
from crewai import Agent
from core.agents.research_crew.research_tools import ResearchTools
from core.config import Config

# 配置日志
logger = logging.getLogger("research_agents")

class ResearchAgents:
    """研究团队智能体定义

    该类负责创建和管理研究团队的各个智能体，包括背景研究员、专家发现者、
    数据分析师和研究报告撰写员。
    """

    _instance: ClassVar[Optional['ResearchAgents']] = None

    @classmethod
    def get_instance(cls, config: Optional[Config] = None) -> 'ResearchAgents':
        """获取ResearchAgents单例实例

        Args:
            config: 可选的配置对象

        Returns:
            ResearchAgents: 单例实例
        """
        if cls._instance is None:
            cls._instance = cls(config=config)
        return cls._instance

    @classmethod
    def clear_instance(cls):
        """清除缓存的单例实例"""
        cls._instance = None

    def __init__(self, config: Optional[Config] = None):
        """初始化智能体管理器

        Args:
            config: 可选的配置对象，如果为None则使用默认配置
        """
        # 加载配置
        self.config = config or Config()

        # 初始化工具集
        logger.info("初始化研究团队工具集...")
        self.tools = ResearchTools(config=self.config)

        # 根据角色创建智能体工具映射
        self.agent_tools = {
            "background_researcher": [
                self.tools.collect_content,
                self.tools.analyze_data,
                self.tools.validate_facts,
                self.tools.search_related_resources
            ],
            "expert_finder": [
                self.tools.search_expert_opinions,
                self.tools.collect_content,
                self.tools.extract_key_findings,
                self.tools.compare_perspectives
            ],
            "data_analyst": [
                self.tools.analyze_data,
                self.tools.collect_content,
                self.tools.extract_key_findings,
                self.tools.analyze_statistics
            ],
            "research_writer": [
                self.tools.generate_research_report,
                self.tools.analyze_data,
                self.tools.extract_key_findings
            ]
        }

        # 智能体角色配置
        self.agent_configs = {
            "background_researcher": {
                "role": "背景研究员",
                "goal": "收集和整理话题的背景信息",
                "backstory": """你是一位专业的背景研究员，擅长收集和整理话题的历史背景、
                发展脉络和现状。你有扎实的研究功底和广泛的知识面，能够快速理解各个领域的基本概念和发展历程。
                你特别注重信息的准确性和完整性，会从多个来源交叉验证信息的可靠性。你的工作为团队提供了
                坚实的研究基础，确保后续分析建立在准确的事实之上。"""
            },
            "expert_finder": {
                "role": "专家发现者",
                "goal": "发现和分析领域专家观点",
                "backstory": """你是一位资深的专家发现者，擅长找出领域内的权威专家和重要观点。
                你有敏锐的判断力，能够辨别真正的专业见解和普通观点。你深知在研究中纳入多元视角的重要性，
                因此总是努力收集不同立场专家的观点进行对比。你善于识别专家言论中的核心洞见，并能有效提取其
                价值所在。你的工作为团队提供了权威的专业视角，大大提升了研究的深度和可信度。"""
            },
            "data_analyst": {
                "role": "数据分析师",
                "goal": "分析和整理研究数据",
                "backstory": """你是一位专业的数据分析师，擅长处理和分析各类研究数据。
                你拥有敏锐的数据洞察能力，能从混乱的信息中识别出有意义的模式和趋势。你熟练运用各种
                分析方法，擅长将复杂数据转化为清晰的见解。你注重数据的可靠性和代表性，始终保持客观和
                严谨的态度。你的工作为团队提供了数据支持的结论，使研究更加科学和可靠。"""
            },
            "research_writer": {
                "role": "研究报告撰写员",
                "goal": "撰写专业的研究报告",
                "backstory": """你是一位专业的研究报告撰写员，擅长将复杂的研究成果转化为清晰的报告。
                你有出色的组织能力和表达能力，能够以逻辑清晰、条理分明的方式呈现复杂信息。你深谙各类
                报告的结构和标准，能根据不同目标受众调整内容深度和表达方式。你特别注重报告的可读性和
                实用性，确保读者能够获取有价值的信息和见解。你的工作将团队的研究成果转化为可行动的知识，
                为决策提供有力支持。"""
            }
        }

        logger.info("研究团队智能体配置初始化完成")

    def create_all_agents(self) -> Dict[str, Agent]:
        """创建所有智能体

        Returns:
            Dict[str, Agent]: 名称到智能体对象的映射
        """
        logger.info("创建所有研究团队智能体...")
        agents = {
            "background_researcher": self.create_background_researcher(),
            "expert_finder": self.create_expert_finder(),
            "data_analyst": self.create_data_analyst(),
            "research_writer": self.create_research_writer()
        }
        logger.info(f"成功创建 {len(agents)} 个研究团队智能体")
        return agents

    def create_background_researcher(self) -> Agent:
        """创建背景研究员智能体

        Returns:
            Agent: 背景研究员智能体
        """
        logger.info("创建背景研究员智能体...")
        config = self.agent_configs["background_researcher"]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=self.agent_tools["background_researcher"],
            verbose=self.config.AGENT_VERBOSE
        )
        logger.info(f"背景研究员智能体创建完成，工具数量: {len(self.agent_tools['background_researcher'])}")
        return agent

    def create_expert_finder(self) -> Agent:
        """创建专家发现者智能体

        Returns:
            Agent: 专家发现者智能体
        """
        logger.info("创建专家发现者智能体...")
        config = self.agent_configs["expert_finder"]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=self.agent_tools["expert_finder"],
            verbose=self.config.AGENT_VERBOSE
        )
        logger.info(f"专家发现者智能体创建完成，工具数量: {len(self.agent_tools['expert_finder'])}")
        return agent

    def create_data_analyst(self) -> Agent:
        """创建数据分析师智能体

        Returns:
            Agent: 数据分析师智能体
        """
        logger.info("创建数据分析师智能体...")
        config = self.agent_configs["data_analyst"]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=self.agent_tools["data_analyst"],
            verbose=self.config.AGENT_VERBOSE
        )
        logger.info(f"数据分析师智能体创建完成，工具数量: {len(self.agent_tools['data_analyst'])}")
        return agent

    def create_research_writer(self) -> Agent:
        """创建研究报告撰写员智能体

        Returns:
            Agent: 研究报告撰写员智能体
        """
        logger.info("创建研究报告撰写员智能体...")
        config = self.agent_configs["research_writer"]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=self.agent_tools["research_writer"],
            verbose=self.config.AGENT_VERBOSE
        )
        logger.info(f"研究报告撰写员智能体创建完成，工具数量: {len(self.agent_tools['research_writer'])}")
        return agent
