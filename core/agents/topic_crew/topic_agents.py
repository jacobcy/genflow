"""选题团队智能体

这个模块定义了选题团队的智能体角色及其配置。
智能体使用专门的工具类提供的工具完成任务，专注于热搜话题分析。
"""
from typing import List, Dict, Any, Optional
import logging
from crewai import Agent
from core.config import Config
from .topic_tools import TopicTools

# 配置日志
logger = logging.getLogger("topic_agents")

class TopicAgents:
    """选题团队智能体定义

    这个类负责创建和配置选题团队的智能体成员。
    当前阶段使用单一智能体"选题顾问"，简化流程。
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化智能体

        Args:
            config: 配置对象，如果为None则创建默认配置
        """
        # 加载配置
        self.config = config or Config()

        # 初始化工具集
        logger.info("初始化选题团队工具集...")
        self.tools = TopicTools(config=self.config)

        # 工具映射 - 只包含热搜相关工具
        self.agent_tools = {
            "topic_advisor": [
                self.tools.get_trending_topics,
                self.tools.get_topic_details,
                self.tools.recommend_topics
            ]
        }

        # 智能体角色配置 - 简化为单一角色
        self.agent_configs = {
            "topic_advisor": {
                "role": "选题顾问",
                "goal": "提供热搜话题建议，辅助人工决策",
                "backstory": """你是一位资深的选题顾问，善于发现和分析热门话题。
                你的主要任务是从各平台热搜中筛选出有价值的话题，为内容创作提供建议。
                你会提供简要分析和建议，但最终决策权在人工编辑手中。
                你的建议简洁明了，重点突出，便于人工快速决策。"""
            }
        }

        logger.info("选题团队智能体初始化完成")

    def create_topic_advisor(self) -> Agent:
        """创建选题顾问智能体

        Returns:
            Agent: 配置好的选题顾问智能体
        """
        logger.info("创建选题顾问智能体...")
        config = self.agent_configs["topic_advisor"]
        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=self.agent_tools["topic_advisor"],
            verbose=True
        )
        logger.info(f"选题顾问智能体创建完成，工具数量: {len(self.agent_tools['topic_advisor'])}")
        return agent

    def create_all_agents(self) -> Dict[str, Agent]:
        """创建所有智能体

        Returns:
            Dict[str, Agent]: 包含所有智能体的字典
        """
        logger.info("创建所有智能体...")
        agents = {
            "topic_advisor": self.create_topic_advisor()
        }
        logger.info(f"成功创建 {len(agents)} 个智能体")
        return agents
