"""审核团队智能体"""
from typing import List, Dict
from crewai import Agent
from src.tools.nlp_tools import NLPAggregator
from src.tools.review_tools.reviewer import (
    PlagiarismChecker,
    StatisticalAIDetector,
    OpenAIDetector,
    SensitiveWordChecker
)

class ReviewAgents:
    """审核团队智能体定义"""
    
    def __init__(self):
        """初始化工具"""
        self.nlp_tools = NLPAggregator()
        self.plagiarism_checker = PlagiarismChecker.get_instance()
        self.statistical_ai_detector = StatisticalAIDetector.get_instance()
        self.openai_detector = OpenAIDetector.get_instance()
        self.sensitive_checker = SensitiveWordChecker.get_instance()
    
    def create_plagiarism_checker(self) -> Agent:
        """创建查重专员"""
        return Agent(
            role='查重专员',
            goal='检查文章的原创性',
            backstory="""你是一位专业的查重专员，擅长发现文章中的重复内容和引用问题。
            你需要仔细检查每一段内容，确保文章符合原创性要求。""",
            tools=[
                self.plagiarism_checker.execute,
                self.nlp_tools.execute
            ]
        )
    
    def create_ai_detector(self) -> Agent:
        """创建AI检测员"""
        return Agent(
            role='AI检测员',
            goal='识别AI生成内容',
            backstory="""你是一位专业的AI内容检测员，擅长识别机器生成的内容。
            你需要分析文章的语言特征，确保内容符合平台对AI生成内容的规范。""",
            tools=[
                self.statistical_ai_detector.execute,
                self.openai_detector.execute,
                self.nlp_tools.execute
            ]
        )
    
    def create_content_reviewer(self) -> Agent:
        """创建内容审核员"""
        return Agent(
            role='内容审核员',
            goal='审核内容合规性',
            backstory="""你是一位经验丰富的内容审核员，擅长发现内容中的敏感信息和不当表述。
            你需要确保文章符合平台的内容规范和法律要求。""",
            tools=[
                self.sensitive_checker.execute,
                self.nlp_tools.execute
            ]
        )
    
    def create_final_reviewer(self) -> Agent:
        """创建终审专员"""
        return Agent(
            role='终审专员',
            goal='全面评估文章质量',
            backstory="""你是一位资深的终审专员，擅长从多个维度评估文章质量。
            你需要整合各方审核意见，给出最终的审核结论和修改建议。""",
            tools=[
                self.nlp_tools.execute,
                self.plagiarism_checker.execute,
                self.sensitive_checker.execute,
                self.statistical_ai_detector.execute
            ]
        ) 