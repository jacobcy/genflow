"""研究团队智能体"""
from typing import List, Dict
from crewai import Agent
from core.tools.content_collectors import ContentCollector
from core.tools.search_tools import SearchAggregator
from core.tools.nlp_tools import NLPAggregator

class ResearchAgents:
    """研究团队智能体定义"""
    
    def __init__(self):
        """初始化工具"""
        self.content_collector = ContentCollector()
        self.search_tools = SearchAggregator()
        self.nlp_tools = NLPAggregator()
    
    def create_background_researcher(self) -> Agent:
        """创建背景研究员"""
        return Agent(
            role='背景研究员',
            goal='收集和整理话题的背景信息',
            backstory="""你是一位专业的背景研究员，擅长收集和整理话题的历史背景、
            发展脉络和现状。你需要确保信息的准确性和完整性。""",
            tools=[
                self.content_collector.execute,
                self.search_tools.execute
            ]
        )
    
    def create_expert_finder(self) -> Agent:
        """创建专家发现者"""
        return Agent(
            role='专家发现者',
            goal='发现和分析领域专家观点',
            backstory="""你是一位资深的专家发现者，擅长找出领域内的权威专家和重要观点。
            你需要收集和分析专家的论述，提取有价值的见解。""",
            tools=[
                self.search_tools.execute,
                self.content_collector.execute
            ]
        )
    
    def create_data_analyst(self) -> Agent:
        """创建数据分析师"""
        return Agent(
            role='数据分析师',
            goal='分析和整理研究数据',
            backstory="""你是一位专业的数据分析师，擅长处理和分析各类研究数据。
            你需要从数据中提取有价值的信息，发现潜在的规律和趋势。""",
            tools=[
                self.nlp_tools.execute,
                self.search_tools.execute
            ]
        )
    
    def create_research_writer(self) -> Agent:
        """创建研究报告撰写员"""
        return Agent(
            role='研究报告撰写员',
            goal='撰写专业的研究报告',
            backstory="""你是一位专业的研究报告撰写员，擅长将复杂的研究成果转化为清晰的报告。
            你需要整合各类信息，生成结构化的研究报告。""",
            tools=[self.nlp_tools.execute]
        ) 