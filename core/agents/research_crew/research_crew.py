"""研究团队管理模块

这个模块定义了研究团队的组织和工作流程，负责协调各个研究智能体的工作，
完成从话题研究到生成研究报告的全流程。
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from crewai import Crew, Task, Agent
from crewai.tasks.task_output import TaskOutput
from core.models.research import ResearchResult, Article, ArticleSection
from core.models.feedback import ResearchFeedback
from core.agents.research_crew.research_agents import ResearchAgents
from core.config import Config

# 配置日志
logger = logging.getLogger("research_crew")

@dataclass
class ResearchWorkflowResult:
    """研究工作流结果模型
    
    保存研究工作流执行的完整结果，包括所有任务输出和最终研究报告
    """
    # 标识信息
    id: str = field(default_factory=lambda: f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = field(default_factory=datetime.now)
    
    # 输入参数
    topic: str = ""
    
    # 工作流执行结果
    background_research: Optional[TaskOutput] = None
    expert_insights: Optional[TaskOutput] = None
    data_analysis: Optional[TaskOutput] = None
    research_report: Optional[TaskOutput] = None
    
    # 最终研究结果
    result: Optional[ResearchResult] = None
    
    # 反馈信息
    feedback: Optional[ResearchFeedback] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式
        
        Returns:
            Dict[str, Any]: 字典形式的结果
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "topic": self.topic,
            "background_research": self.background_research.raw_output if self.background_research else None,
            "expert_insights": self.expert_insights.raw_output if self.expert_insights else None,
            "data_analysis": self.data_analysis.raw_output if self.data_analysis else None,
            "research_report": self.research_report.raw_output if self.research_report else None,
            "result": self.result.to_dict() if self.result else None,
            "feedback": self.feedback.to_dict() if self.feedback else None
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串
        
        Returns:
            str: JSON字符串形式的结果
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def save_to_file(self, filepath: str) -> None:
        """保存结果到文件
        
        Args:
            filepath: 文件路径
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        logger.info(f"研究工作流结果已保存到文件: {filepath}")


class ResearchCrew:
    """研究团队类
    
    这个类管理研究团队的组织结构和工作流程，负责协调各个研究智能体的工作。
    它处理从话题研究到生成研究报告的全流程，包括获取人类反馈和生成文章大纲。
    """
    
    def __init__(self, config: Optional[Config] = None):
        """初始化研究团队
        
        Args:
            config: 可选的配置对象，如果为None则使用默认配置
        """
        # 加载配置
        self.config = config or Config()
        logger.info("初始化研究团队...")
        
        # 创建智能体管理器
        self.agent_manager = ResearchAgents.get_instance(config=self.config)
        
        # 获取所有智能体
        self.agents = self.agent_manager.create_all_agents()
        logger.info(f"研究团队初始化完成，包含 {len(self.agents)} 个智能体")
        
        # 记录最近执行的工作流结果
        self.last_workflow_result = None
    
    def _create_background_research_task(self, topic: str) -> Task:
        """创建背景研究任务
        
        Args:
            topic: 研究话题
            
        Returns:
            Task: 背景研究任务
        """
        logger.info(f"创建背景研究任务，话题: {topic}")
        return Task(
            description=f"""
            对话题"{topic}"进行全面的背景研究。
            
            你的任务是:
            1. 收集该话题的基本背景信息，包括历史发展、重要事件和时间线
            2. 确定该话题的关键概念、术语和基础知识
            3. 找出该话题的主要争议点或挑战
            4. 分析该话题的当前发展状态和趋势
            5. 整理相关的基础统计数据和事实
            
            输出应为一份结构化的背景研究报告，包含以下部分:
            - 话题概述
            - 历史背景与发展
            - 关键概念与术语
            - 主要争议点或挑战
            - 当前状态与趋势
            - 基础统计数据
            
            确保信息准确可靠，并尽可能引用来源。
            """,
            expected_output="一份详尽的背景研究报告，包含指定的所有部分，不少于1500字",
            agent=self.agents["background_researcher"],
            context=[
                {"role": "system", "content": f"你正在研究话题: {topic}。请记住保持客观中立的立场，关注事实而非观点。"}
            ]
        )
    
    def _create_expert_finder_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建专家发现任务
        
        Args:
            topic: 研究话题
            background_research: 背景研究结果
            
        Returns:
            Task: 专家发现任务
        """
        logger.info(f"创建专家发现任务，话题: {topic}")
        return Task(
            description=f"""
            为话题"{topic}"寻找并分析领域专家的观点和见解。
            
            你的任务是:
            1. 识别该话题领域的3-5位权威专家
            2. 收集并整理这些专家对该话题的主要观点和见解
            3. 分析专家观点之间的共识和分歧
            4. 评估这些专家观点的可信度和影响力
            5. 提取对研究最有价值的专家洞见
            
            参考背景研究报告以确保你找到的专家与话题紧密相关。
            
            输出应为一份专家观点分析报告，包含以下部分:
            - 专家概述(姓名、背景、专长)
            - 各专家主要观点摘要
            - 专家观点的共识和分歧分析
            - 专家观点的可信度评估
            - 对研究最有价值的关键洞见
            
            确保引用专家观点的来源和时间。
            """,
            expected_output="一份专家观点分析报告，包含指定的所有部分，不少于1200字",
            agent=self.agents["expert_finder"],
            context=[
                {"role": "system", "content": f"你正在寻找话题'{topic}'的专家观点。请确保收集多元观点，不要只关注单一立场的专家。"},
                {"role": "user", "content": f"这是话题的背景研究报告，请参考以便更准确地找到相关专家:\n\n{background_research.raw_output}"}
            ]
        )
    
    def _create_data_analysis_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建数据分析任务
        
        Args:
            topic: 研究话题
            background_research: 背景研究结果
            
        Returns:
            Task: 数据分析任务
        """
        logger.info(f"创建数据分析任务，话题: {topic}")
        return Task(
            description=f"""
            对话题"{topic}"的相关数据进行深入分析。
            
            你的任务是:
            1. 分析与该话题相关的关键数据和统计信息
            2. 识别数据中的模式、趋势和关联
            3. 提取支持或反驳主要观点的数据证据
            4. 评估数据的可靠性和代表性
            5. 生成对研究有价值的数据洞察
            
            参考背景研究报告以确保你的分析与话题紧密相关。
            
            输出应为一份数据分析报告，包含以下部分:
            - 分析摘要
            - 关键数据点和统计信息
            - 模式和趋势分析
            - 数据支持的主要发现
            - 数据局限性说明
            - 基于数据的建议或预测
            
            确保清晰说明数据来源和分析方法。
            """,
            expected_output="一份数据分析报告，包含指定的所有部分，不少于1000字",
            agent=self.agents["data_analyst"],
            context=[
                {"role": "system", "content": f"你正在分析话题'{topic}'的相关数据。请保持客观，避免数据过度解读或选择性引用。"},
                {"role": "user", "content": f"这是话题的背景研究报告，请参考以便进行更有针对性的数据分析:\n\n{background_research.raw_output}"}
            ]
        )
    
    def _create_research_report_task(
        self, 
        topic: str, 
        background_research: TaskOutput, 
        expert_insights: TaskOutput, 
        data_analysis: TaskOutput
    ) -> Task:
        """创建研究报告撰写任务
        
        Args:
            topic: 研究话题
            background_research: 背景研究结果
            expert_insights: 专家洞见结果
            data_analysis: 数据分析结果
            
        Returns:
            Task: 研究报告撰写任务
        """
        logger.info(f"创建研究报告撰写任务，话题: {topic}")
        return Task(
            description=f"""
            为话题"{topic}"撰写一份综合研究报告。
            
            你的任务是:
            1. 整合背景研究、专家洞见和数据分析的结果
            2. 形成对话题的全面、深入和客观的分析
            3. 提出有支持证据的结论和建议
            4. 确保报告结构清晰、逻辑严密且易于理解
            5. 标注信息来源和参考文献
            
            你将获得背景研究报告、专家观点分析和数据分析报告作为输入。
            
            输出应为一份完整的研究报告，包含以下部分:
            - 执行摘要
            - 引言(研究背景和目的)
            - 研究方法
            - 主要发现(分主题组织)
            - 讨论和分析
            - 结论和建议
            - 参考资料
            
            确保报告内容客观中立，观点有据可依，并适当引用背景研究、专家观点和数据分析中的信息。
            """,
            expected_output="一份完整的研究报告，包含指定的所有部分，不少于3000字",
            agent=self.agents["research_writer"],
            context=[
                {"role": "system", "content": f"你正在撰写话题'{topic}'的综合研究报告。请确保报告逻辑连贯，观点平衡，证据充分。"},
                {"role": "user", "content": f"这是背景研究报告:\n\n{background_research.raw_output}"},
                {"role": "user", "content": f"这是专家观点分析报告:\n\n{expert_insights.raw_output}"},
                {"role": "user", "content": f"这是数据分析报告:\n\n{data_analysis.raw_output}"}
            ]
        )
    
    def research_topic(self, topic: str, progress_callback=None) -> ResearchResult:
        """研究指定话题并生成研究报告
        
        Args:
            topic: 研究话题
            progress_callback: 可选的进度回调函数，接收(current_step, total_steps, step_name)参数
            
        Returns:
            ResearchResult: 研究结果对象
        """
        logger.info(f"开始研究话题: {topic}")
        workflow_result = ResearchWorkflowResult(topic=topic)
        
        # 定义工作流步骤
        total_steps = 4
        current_step = 0
        
        # 第1步: 背景研究
        current_step += 1
        step_name = "背景研究"
        if progress_callback:
            progress_callback(current_step, total_steps, step_name)
        logger.info(f"开始第{current_step}步: {step_name}")
        
        background_task = self._create_background_research_task(topic)
        crew = Crew(
            agents=[self.agents["background_researcher"]],
            tasks=[background_task],
            verbose=self.config.CREW_VERBOSE
        )
        background_research = crew.kickoff()
        workflow_result.background_research = background_research
        logger.info(f"完成第{current_step}步: {step_name}")
        
        # 第2步: 专家洞见
        current_step += 1
        step_name = "专家洞见"
        if progress_callback:
            progress_callback(current_step, total_steps, step_name)
        logger.info(f"开始第{current_step}步: {step_name}")
        
        expert_task = self._create_expert_finder_task(topic, background_research)
        crew = Crew(
            agents=[self.agents["expert_finder"]],
            tasks=[expert_task],
            verbose=self.config.CREW_VERBOSE
        )
        expert_insights = crew.kickoff()
        workflow_result.expert_insights = expert_insights
        logger.info(f"完成第{current_step}步: {step_name}")
        
        # 第3步: 数据分析
        current_step += 1
        step_name = "数据分析"
        if progress_callback:
            progress_callback(current_step, total_steps, step_name)
        logger.info(f"开始第{current_step}步: {step_name}")
        
        data_task = self._create_data_analysis_task(topic, background_research)
        crew = Crew(
            agents=[self.agents["data_analyst"]],
            tasks=[data_task],
            verbose=self.config.CREW_VERBOSE
        )
        data_analysis = crew.kickoff()
        workflow_result.data_analysis = data_analysis
        logger.info(f"完成第{current_step}步: {step_name}")
        
        # 第4步: 研究报告
        current_step += 1
        step_name = "研究报告"
        if progress_callback:
            progress_callback(current_step, total_steps, step_name)
        logger.info(f"开始第{current_step}步: {step_name}")
        
        report_task = self._create_research_report_task(
            topic, background_research, expert_insights, data_analysis
        )
        crew = Crew(
            agents=[self.agents["research_writer"]],
            tasks=[report_task],
            verbose=self.config.CREW_VERBOSE
        )
        research_report = crew.kickoff()
        workflow_result.research_report = research_report
        logger.info(f"完成第{current_step}步: {step_name}")
        
        # 创建最终研究结果对象
        result = ResearchResult(
            topic=topic,
            background_research=background_research.raw_output,
            expert_insights=expert_insights.raw_output,
            data_analysis=data_analysis.raw_output,
            research_report=research_report.raw_output
        )
        workflow_result.result = result
        
        # 保存工作流结果
        self.last_workflow_result = workflow_result
        
        logger.info(f"话题'{topic}'的研究已完成")
        return result
    
    def run_full_workflow(self, topic: str, progress_callback=None) -> Tuple[ResearchResult, Article]:
        """运行完整的研究工作流，包括研究和文章大纲生成
        
        Args:
            topic: 研究话题
            progress_callback: 可选的进度回调函数，接收(current_step, total_steps, step_name)参数
            
        Returns:
            Tuple[ResearchResult, Article]: 研究结果和文章大纲
        """
        logger.info(f"开始完整研究工作流，话题: {topic}")
        
        # 定义工作流步骤
        total_steps = 5
        current_step = 0
        
        # 步骤1-4: 研究话题
        research_result = self.research_topic(
            topic, 
            progress_callback=lambda step, total, name: progress_callback(step, total_steps, name) if progress_callback else None
        )
        
        # 步骤5: 生成文章大纲
        current_step = 5
        step_name = "生成文章大纲"
        if progress_callback:
            progress_callback(current_step, total_steps, step_name)
        logger.info(f"开始第{current_step}步: {step_name}")
        
        article = self.generate_article_outline(research_result)
        logger.info(f"完成第{current_step}步: {step_name}")
        
        logger.info(f"话题'{topic}'的完整研究工作流已完成")
        return research_result, article
    
    def get_human_feedback(self, result: ResearchResult) -> ResearchFeedback:
        """获取研究结果的人类反馈
        
        Args:
            result: 研究结果对象
            
        Returns:
            ResearchFeedback: 反馈对象
        """
        logger.info("开始收集研究结果的人类反馈")
        
        # 在实际应用中，这里应该调用某种用户界面来收集反馈
        # 这里我们返回一个样例反馈
        feedback = ResearchFeedback(
            background_research_score=4,
            background_research_comments="背景研究全面且深入，但缺少一些最新的发展",
            expert_insights_score=5,
            expert_insights_comments="专家观点多元且具有代表性，分析深刻",
            data_analysis_score=4,
            data_analysis_comments="数据分析严谨，但可以增加更多图表支持",
            overall_score=4.5,
            overall_comments="整体研究质量高，结构清晰，观点平衡",
            suggested_improvements=["增加最新行业发展趋势", "加强数据可视化", "扩展解决方案分析"]
        )
        
        # 如果有上次工作流结果，则更新反馈
        if self.last_workflow_result and self.last_workflow_result.result == result:
            self.last_workflow_result.feedback = feedback
        
        logger.info("人类反馈收集完成")
        return feedback
    
    def generate_article_outline(self, research_result: ResearchResult) -> Article:
        """基于研究结果生成文章大纲
        
        Args:
            research_result: 研究结果对象
            
        Returns:
            Article: 文章大纲对象
        """
        logger.info(f"开始为话题'{research_result.topic}'生成文章大纲")
        
        # 从研究报告中提取主要部分
        # 在实际应用中，这里应该使用更复杂的逻辑来分析研究报告并提取结构化信息
        # 这里使用简化的逻辑
        
        # 创建文章对象
        article = Article(
            title=f"{research_result.topic} - 研究分析",
            description=f"基于深入研究对{research_result.topic}的全面分析和见解",
            keywords=[research_result.topic] + research_result.topic.split()[:3],
            sections=[]
        )
        
        # 添加引言部分
        article.sections.append(
            ArticleSection(
                title="引言",
                content=f"介绍{research_result.topic}的背景和重要性",
                key_points=[
                    "话题背景和上下文",
                    "为什么这个话题重要",
                    "本文的研究范围和目标"
                ]
            )
        )
        
        # 从研究报告中提取三个主要部分作为文章章节
        main_sections = self._extract_main_sections_from_report(research_result.research_report)
        for section in main_sections:
            article.sections.append(section)
        
        # 添加结论部分
        article.sections.append(
            ArticleSection(
                title="结论与展望",
                content=f"总结关于{research_result.topic}的主要发现和未来展望",
                key_points=[
                    "研究的主要发现和结论",
                    "对未来发展的预测",
                    "值得进一步研究的方向"
                ]
            )
        )
        
        logger.info(f"文章大纲生成完成，包含 {len(article.sections)} 个章节")
        return article
    
    def _extract_main_sections_from_report(self, report: str) -> List[ArticleSection]:
        """从研究报告中提取主要章节
        
        Args:
            report: 研究报告文本
            
        Returns:
            List[ArticleSection]: 提取的文章章节列表
        """
        # 在实际应用中，这里应该使用NLP技术分析报告结构并提取章节
        # 这里使用简化的逻辑创建示例章节
        
        # 创建三个样例章节
        sections = [
            ArticleSection(
                title="背景与历史发展",
                content="详述话题的历史背景和发展脉络",
                key_points=[
                    "起源和历史发展",
                    "关键事件和里程碑",
                    "历史演变中的重要转折点"
                ]
            ),
            ArticleSection(
                title="专家观点分析",
                content="分析领域专家对话题的不同见解和立场",
                key_points=[
                    "主流专家观点概述",
                    "不同学派或立场的比较",
                    "观点争议和共识点"
                ]
            ),
            ArticleSection(
                title="数据支持的关键发现",
                content="基于数据分析提出的主要发现和洞见",
                key_points=[
                    "关键统计数据和趋势",
                    "数据支持的主要论点",
                    "数据解读和启示"
                ]
            )
        ]
        
        return sections 