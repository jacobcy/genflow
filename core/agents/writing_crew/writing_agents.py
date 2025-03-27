"""写作团队智能体模块

定义了写作团队中的各个智能体角色及其能力。
"""
import logging
from typing import List, Dict, Optional
from crewai import Agent
from core.models.platform import Platform
from .writing_tools import WritingTools

# 配置日志
logger = logging.getLogger(__name__)

class WritingAgents:
    """写作团队智能体管理类

    负责创建和管理写作流程中的各个角色智能体。
    遵循CrewAI最佳实践，每个智能体都有明确的角色定位和合适的工具集。
    """

    def __init__(self):
        """初始化写作智能体管理器"""
        logger.info("初始化写作智能体管理器")

        # 创建写作工具集
        self.tools = WritingTools()

        # 智能体角色与能力配置
        self.role_configs = {
            "outline_creator": {
                "role": "大纲设计师",
                "goal": "创建清晰、有吸引力且结构合理的文章大纲",
                "backstory": """你是一位资深内容架构专家，擅长设计引人入胜的文章结构。
                你熟悉各种内容平台的要求，能够为不同类型的文章设计出最适合的结构。
                你关注读者体验，确保内容逻辑流畅，重点突出。""",
                "tools": [
                    self.tools.analyze_structure,
                    self.tools.extract_keywords
                ]
            },
            "content_writer": {
                "role": "内容创作者",
                "goal": "根据大纲创作专业、生动且信息丰富的文章内容",
                "backstory": """你是一位才华横溢的内容创作者，擅长将复杂概念转化为易于理解的内容。
                你的文章不仅内容丰富，而且表达生动，能够长时间吸引读者注意力。
                你重视事实准确性，同时注重叙事流畅性和表达的多样性。""",
                "tools": [
                    self.tools.write_article,
                    self.tools.adapt_style
                ]
            },
            "seo_specialist": {
                "role": "SEO优化专家",
                "goal": "优化内容以提高搜索引擎可见性和点击率",
                "backstory": """你是一位经验丰富的SEO专家，精通搜索引擎算法和内容优化技巧。
                你能够在保持内容质量的同时，提升其在搜索结果中的排名。
                你关注关键词密度和标题优化""",
                "tools": [
                    self.tools.optimize_seo,
                    self.tools.extract_keywords,
                    self.tools.summarize_content
                ]
            },
            "editor": {
                "role": "内容编辑",
                "goal": "提升内容质量，确保语法正确、表达清晰并符合平台风格",
                "backstory": """你是一位精益求精的资深编辑，擅长发现并修正内容中的各种问题。
                你注重细节，能够捕捉到微小的语法错误和逻辑不一致。
                你既有语言专家的敏锐，又有读者的视角，能使内容更加流畅易读。""",
                "tools": [
                    self.tools.edit_article,
                    self.tools.adapt_style,
                    self.tools.analyze_structure
                ]
            },
            "fact_checker": {
                "role": "事实核查员",
                "goal": "确保文章中的事实和数据准确无误",
                "backstory": """你是一位严谨的事实核查专家，对数据和事实有着近乎苛刻的要求。
                你善于识别可疑信息，并通过多种渠道验证内容的准确性。
                你相信真实是内容价值的基础，不放过任何一处可能的错误。""",
                "tools": [
                    self.tools.analyze_structure
                ]
            }
        }

        # 初始化智能体实例
        self.agents = {}
        logger.info("写作智能体配置完成")

    def create_agent(self, role_key: str, verbose: bool = True) -> Agent:
        """
        创建指定角色的智能体

        Args:
            role_key: 角色键名，对应role_configs中的配置
            verbose: 是否启用详细日志

        Returns:
            Agent: 创建的智能体实例
        """
        if role_key not in self.role_configs:
            logger.error(f"未找到角色配置: {role_key}")
            raise ValueError(f"未找到角色配置: {role_key}")

        config = self.role_configs[role_key]
        logger.info(f"创建{config['role']}智能体")

        agent = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=config["tools"],
            verbose=verbose,
            allow_delegation=True
        )

        # 缓存创建的智能体
        self.agents[role_key] = agent
        logger.info(f"{config['role']}智能体创建完成，分配了{len(config['tools'])}个工具")

        return agent

    def get_outline_creator(self, verbose: bool = True) -> Agent:
        """获取大纲设计师智能体"""
        return self.create_agent("outline_creator", verbose)

    def get_content_writer(self, verbose: bool = True) -> Agent:
        """获取内容创作者智能体"""
        return self.create_agent("content_writer", verbose)

    def get_seo_specialist(self, verbose: bool = True) -> Agent:
        """获取SEO优化专家智能体"""
        return self.create_agent("seo_specialist", verbose)

    def get_editor(self, verbose: bool = True) -> Agent:
        """获取内容编辑智能体"""
        return self.create_agent("editor", verbose)

    def get_fact_checker(self, verbose: bool = True) -> Agent:
        """获取事实核查员智能体"""
        return self.create_agent("fact_checker", verbose)

    # 保留以下方法以兼容旧代码
    def create_outline_creator(self, verbose: bool = True) -> Agent:
        """创建大纲设计师智能体"""
        return self.get_outline_creator(verbose)

    def create_content_writer(self, verbose: bool = True) -> Agent:
        """创建内容创作者智能体"""
        return self.get_content_writer(verbose)

    def create_seo_specialist(self, verbose: bool = True) -> Agent:
        """创建SEO优化专家智能体"""
        return self.get_seo_specialist(verbose)

    def create_editor(self, verbose: bool = True) -> Agent:
        """创建内容编辑智能体"""
        return self.get_editor(verbose)

    def create_fact_checker(self, verbose: bool = True) -> Agent:
        """创建事实核查员智能体"""
        return self.get_fact_checker(verbose)

    def create_all_agents(self, verbose: bool = True) -> Dict[str, Agent]:
        """创建所有智能体"""
        logger.info("创建所有写作智能体")

        for role_key in self.role_configs.keys():
            self.create_agent(role_key, verbose)

        logger.info(f"已创建{len(self.agents)}个写作智能体")
        return self.agents
