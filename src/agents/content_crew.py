"""CrewAI 内容生成工作流"""
from typing import List, Dict, Any, Optional
from crewai import Agent, Task, Crew, Process
from src.tools.content_collectors import ContentCollector
from src.tools.search_tools import SearchAggregator
from src.tools.nlp_tools import NLPAggregator
from src.tools.style_tools import StyleAdapter
from src.tools.review_tools.reviewer import (
    PlagiarismChecker,
    StatisticalAIDetector,
    OpenAIDetector,
    SensitiveWordChecker
)

class ContentCrew:
    """内容生成团队"""
    
    def __init__(self):
        try:
            # 基础工具
            self.content_collector = ContentCollector()
            self.search_tools = SearchAggregator()
            self.nlp_tools = NLPAggregator()
            
            # 风格工具
            self.style_adapter = StyleAdapter.get_instance()
            
            # 审核工具
            self.plagiarism_checker = PlagiarismChecker.get_instance()
            self.ai_detector = StatisticalAIDetector.get_instance()
            self.openai_detector = OpenAIDetector.get_instance()
            self.sensitive_checker = SensitiveWordChecker.get_instance()
            
            # 初始化智能体
            self._init_agents()
        except Exception as e:
            raise RuntimeError(f"初始化ContentCrew失败: {str(e)}")
    
    def _init_agents(self):
        """初始化所有智能体"""
        try:
            self.researcher = self._create_researcher()
            self.writer = self._create_writer()
            self.stylist = self._create_stylist()
            self.reviewer = self._create_reviewer()
            self.editor = self._create_editor()
        except Exception as e:
            raise RuntimeError(f"初始化智能体失败: {str(e)}")
    
    def _create_researcher(self) -> Agent:
        """创建研究员智能体"""
        return Agent(
            role='研究员',
            goal='深入研究主题,收集高质量的相关资料',
            backstory="""你是一位经验丰富的研究员,擅长信息检索和内容分析。
            你的职责是确保收集到的每一份资料都准确、可靠且与主题高度相关。""",
            tools=[
                self.search_tools.execute,
                self.content_collector.execute
            ],
            verbose=True
        )
    
    def _create_writer(self) -> Agent:
        """创建写作者智能体"""
        return Agent(
            role='写作者',
            goal='基于研究材料创作高质量的原创内容',
            backstory="""你是一位专业的内容创作者,擅长将复杂的信息转化为清晰、
            引人入胜的文章。你注重内容的逻辑性和可读性。""",
            tools=[self.nlp_tools.execute],
            verbose=True
        )
        
    def _create_stylist(self) -> Agent:
        """创建风格优化师智能体"""
        return Agent(
            role='风格优化师',
            goal='优化内容风格，适配目标平台',
            backstory="""你是一位专业的内容风格优化师，精通各大平台的内容特点。
            你的职责是确保内容风格符合目标平台的要求，提升内容的传播效果。""",
            tools=[self.style_adapter.execute],
            verbose=True
        )
        
    def _create_reviewer(self) -> Agent:
        """创建内容审核员智能体"""
        return Agent(
            role='内容审核员',
            goal='全面审核内容质量和合规性',
            backstory="""你是一位严谨的内容审核员，负责确保内容的原创性和合规性。
            你需要进行查重检测、AI生成检测和敏感词检查。""",
            tools=[
                self.plagiarism_checker.execute,
                self.ai_detector.execute,
                self.openai_detector.execute,
                self.sensitive_checker.execute
            ],
            verbose=True
        )
    
    def _create_editor(self) -> Agent:
        """创建编辑智能体"""
        return Agent(
            role='编辑',
            goal='确保内容的最终质量',
            backstory="""你是一位资深的编辑,负责内容的最终把关。
            你需要综合考虑内容质量、表达方式、审核意见，给出最终修改建议。""",
            tools=[
                self.nlp_tools.execute,
                self.style_adapter.execute
            ],
            verbose=True
        )
    
    def create_content(self, topic: str, platform: str = "default") -> Dict[str, Any]:
        """创建内容的主要流程
        
        Args:
            topic: 要创作的主题
            platform: 目标平台
            
        Returns:
            Dict[str, Any]: 包含最终内容和元数据的字典
            
        Raises:
            RuntimeError: 如果内容生成过程中出现错误
        """
        try:
            # 创建任务
            tasks = self._create_tasks(topic, platform)
            
            # 创建工作流
            crew = Crew(
                agents=[
                    self.researcher,
                    self.writer,
                    self.stylist,
                    self.reviewer,
                    self.editor
                ],
                tasks=tasks,
                process=Process.sequential,  # 按顺序执行任务
                verbose=True
            )
            
            # 执行工作流
            result = crew.kickoff()
            
            return self._create_response(result, topic, platform)
            
        except Exception as e:
            raise RuntimeError(f"内容生成失败: {str(e)}")
    
    def _create_tasks(self, topic: str, platform: str) -> List[Task]:
        """创建任务列表"""
        return [
            Task(
                description=f"""
                1. 使用搜索工具收集关于"{topic}"的相关信息
                2. 访问搜索结果中的重要链接,提取有价值的内容
                3. 整理收集到的信息,确保信息的完整性和可靠性
                4. 输出研究报告,包含主要发现和关键信息
                """,
                agent=self.researcher
            ),
            Task(
                description=f"""
                1. 仔细阅读研究报告,理解主题的核心内容
                2. 使用NLP工具分析材料,提取关键概念和观点
                3. 组织内容大纲,确保逻辑清晰
                4. 创作原创内容,确保内容的准确性和可读性
                """,
                agent=self.writer
            ),
            Task(
                description=f"""
                1. 分析目标平台"{platform}"的内容特点
                2. 根据平台特点优化内容风格
                3. 调整内容结构和表达方式
                4. 确保内容符合平台调性
                """,
                agent=self.stylist
            ),
            Task(
                description=f"""
                1. 使用查重工具检查内容原创性
                2. 使用AI检测工具分析内容特征
                3. 进行敏感词检查
                4. 生成完整的审核报告
                """,
                agent=self.reviewer
            ),
            Task(
                description=f"""
                1. 审查文章内容和审核报告
                2. 根据审核意见优化内容
                3. 确保内容的整体质量
                4. 给出最终修改建议和确认
                """,
                agent=self.editor
            )
        ]
    
    def _create_response(self, result: str, topic: str, platform: str) -> Dict[str, Any]:
        """创建响应数据"""
        return {
            "content": result,
            "metadata": {
                "topic": topic,
                "platform": platform,
                "process": "research -> writing -> style -> review -> editing",
                "tools_used": [
                    "SearchAggregator",
                    "ContentCollector",
                    "NLPAggregator",
                    "StyleAdapter",
                    "PlagiarismChecker",
                    "AIDetector",
                    "SensitiveWordChecker"
                ],
                "status": "success"
            }
        }

def main():
    """主函数"""
    try:
        crew = ContentCrew()
        result = crew.create_content(
            topic="Python异步编程最佳实践",
            platform="zhihu"  # 指定目标平台
        )
        print(f"生成内容: {result['content']}")
        print(f"元数据: {result['metadata']}")
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 