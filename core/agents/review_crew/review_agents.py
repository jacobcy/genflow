"""审核团队智能体模块

定义了审核团队中的各个智能体角色及其能力。
"""
import logging
from typing import List, Dict, Optional
from crewai import Agent
from core.models.platform import Platform
from .review_tools import ReviewTools

# 配置日志
logger = logging.getLogger(__name__)

class ReviewAgents:
    """审核团队智能体管理类
    
    负责创建和管理审核流程中的各个角色智能体。
    遵循CrewAI最佳实践，每个智能体都有明确的角色定位和合适的工具集。
    """

    def __init__(self, platform: Platform):
        """初始化审核智能体管理器
        
        Args:
            platform: 目标发布平台，决定了内容规范和审核标准
        """
        logger.info(f"初始化审核智能体管理器，目标平台: {platform.name}")
        self.platform = platform
        
        # 创建审核工具集
        self.tools = ReviewTools(platform)
        
        # 智能体角色与能力配置
        self.role_configs = {
            "plagiarism_checker": {
                "role": "查重专员",
                "goal": "检查文章的原创性和引用规范",
                "backstory": """你是一位专业的查重专员，擅长发现文章中的重复内容和引用问题。
                你对学术诚信和原创性有着极高的要求，能够识别各种形式的抄袭和不当引用。
                你的职责是确保内容满足原创性标准，并提供具体的改进建议。""",
                "tools": [
                    self.tools.check_plagiarism,
                    self.tools.analyze_content_quality
                ]
            },
            "ai_detector": {
                "role": "AI检测员",
                "goal": "识别AI生成内容并评估其符合平台规范的程度",
                "backstory": """你是一位专业的AI内容检测员，精通各种AI生成文本的特征识别。
                你能准确区分人工创作和机器生成的内容，并了解不同平台对AI内容的政策规定。
                你的职责是评估内容的AI特征，确保符合平台对AI生成内容的规范要求。""",
                "tools": [
                    self.tools.detect_ai_content,
                    self.tools.analyze_content_quality
                ]
            },
            "content_reviewer": {
                "role": "内容审核员",
                "goal": "审核内容合规性和敏感信息",
                "backstory": """你是一位经验丰富的内容审核员，熟悉各类媒体平台的内容政策和法律法规。
                你擅长识别各种敏感信息、不当表述和潜在风险内容。
                你的职责是确保内容合规，避免任何可能导致平台风险的表述和信息。""",
                "tools": [
                    self.tools.check_sensitive_content,
                    self.tools.evaluate_compliance
                ]
            },
            "quality_assessor": {
                "role": "质量评估师",
                "goal": "评估内容的专业性、准确性和整体质量",
                "backstory": """你是一位内容质量评估专家，具有广泛的知识背景和严格的质量标准。
                你关注内容的深度、准确性、结构合理性和专业表达。
                你的职责是全面评估内容质量，确保达到专业出版标准。""",
                "tools": [
                    self.tools.analyze_content_quality,
                    self.tools.evaluate_compliance
                ]
            },
            "final_reviewer": {
                "role": "终审专员",
                "goal": "整合各方审核结果，做出最终审核决定",
                "backstory": """你是一位经验丰富的终审专员，擅长综合分析和决策。
                你具有出色的判断力，能够平衡内容价值与合规要求。
                你的职责是综合各项审核结果，给出最终的审核决定和改进建议。""",
                "tools": [
                    self.tools.generate_review_report,
                    self.tools.evaluate_compliance,
                    self.tools.check_plagiarism,
                    self.tools.detect_ai_content,
                    self.tools.check_sensitive_content
                ]
            }
        }
        
        # 初始化智能体实例
        self.agents = {}
        logger.info("审核智能体配置完成")

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
    
    def create_plagiarism_checker(self, verbose: bool = True) -> Agent:
        """创建查重专员智能体"""
        return self.create_agent("plagiarism_checker", verbose)
    
    def create_ai_detector(self, verbose: bool = True) -> Agent:
        """创建AI检测员智能体"""
        return self.create_agent("ai_detector", verbose)
    
    def create_content_reviewer(self, verbose: bool = True) -> Agent:
        """创建内容审核员智能体"""
        return self.create_agent("content_reviewer", verbose)
    
    def create_quality_assessor(self, verbose: bool = True) -> Agent:
        """创建质量评估师智能体"""
        return self.create_agent("quality_assessor", verbose)
    
    def create_final_reviewer(self, verbose: bool = True) -> Agent:
        """创建终审专员智能体"""
        return self.create_agent("final_reviewer", verbose)
    
    def create_all_agents(self, verbose: bool = True) -> Dict[str, Agent]:
        """创建所有智能体
        
        Returns:
            Dict[str, Agent]: 所有创建的智能体
        """
        logger.info("创建所有审核智能体")
        
        for role_key in self.role_configs.keys():
            self.create_agent(role_key, verbose)
            
        logger.info(f"已创建{len(self.agents)}个审核智能体")
        return self.agents 