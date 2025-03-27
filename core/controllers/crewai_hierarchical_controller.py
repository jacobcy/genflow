"""CrewAI层次流程控制器

该模块使用CrewAI的Hierarchical Process实现内容生产流程，
通过管理Agent动态协调和分配任务，实现更灵活的内容生产。
集成Flow API实现完整的状态管理。
"""

import logging
import os
import asyncio
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, listen, start

from core.models.topic import Topic
from core.models.article import Article
from core.models.platform import Platform, get_default_platform
from core.models.progress import ProductionProgress, ProductionStage

logger = logging.getLogger(__name__)

class ManagerProductionState(BaseModel):
    """层次流程内容生产状态模型"""
    # 输入参数
    category: str = ""
    style: Optional[str] = None
    platform_name: str = "default"
    article: Optional[Article] = None  # 添加文章引用

    # 任务执行相关
    task_results: Dict[str, Any] = Field(default_factory=dict)
    delegated_tasks: List[str] = Field(default_factory=list)
    tasks_completed: List[str] = Field(default_factory=list)

    # 生产结果
    final_output: Optional[Any] = None
    manager_analysis: Optional[str] = None  # 管理Agent的分析结果

    # 监控数据
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_stage: str = "initialized"  # initialized, running, completed, failed
    status: str = "pending"  # pending, running, completed, failed, cancelled
    error: Optional[str] = None

    # 执行统计
    execution_time: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)

    def mark_start(self):
        """标记开始时间"""
        self.started_at = datetime.now()
        self.status = "running"
        self.current_stage = "running"
        # 同步文章状态
        if self.article:
            from core.models.content_manager import ContentManager
            ContentManager.update_article_status(self.article, "running")

    def mark_complete(self):
        """标记完成时间"""
        self.completed_at = datetime.now()
        self.status = "completed"
        self.current_stage = "completed"
        # 同步文章状态
        if self.article:
            from core.models.content_manager import ContentManager
            ContentManager.update_article_status(self.article, "completed")

    def mark_failed(self, error_msg: str):
        """标记失败状态"""
        self.status = "failed"
        self.current_stage = "failed"
        self.error = error_msg
        # 同步文章状态
        if self.article:
            from core.models.content_manager import ContentManager
            ContentManager.update_article_status(self.article, "failed")

    def mark_cancelled(self):
        """标记取消状态"""
        self.status = "cancelled"
        self.current_stage = "cancelled"
        # 同步文章状态
        if self.article:
            from core.models.content_manager import ContentManager
            ContentManager.update_article_status(self.article, "cancelled")

    def add_task_result(self, task_name: str, result: Any):
        """添加任务结果"""
        self.task_results[task_name] = result
        self.tasks_completed.append(task_name)

    def add_delegated_task(self, task_name: str):
        """添加委派的任务"""
        self.delegated_tasks.append(task_name)

class CrewAIManagerController(Flow[ManagerProductionState]):
    """使用CrewAI层次流程的内容生产控制器

    通过CrewAI的Hierarchical Process实现内容生产，
    由管理Agent动态协调和分配任务给专家团队，实现灵活内容生产。
    集成Flow API实现状态管理。
    """

    def __init__(self, model_name="gpt-4"):
        """初始化层次流程控制器

        Args:
            model_name: Agent使用的LLM模型名称
        """
        super().__init__()
        self.model_name = model_name
        self.current_progress = None
        self.platform = None

    async def initialize(self, platform: Optional[Platform] = None):
        """初始化控制器

        Args:
            platform: 目标平台，如果不提供则使用默认配置
        """
        self.platform = platform or get_default_platform()
        logger.info(f"CrewAI层次流程控制器已初始化，使用模型: {self.model_name}")
        self.current_progress = ProductionProgress()

        # 设置平台信息到状态
        if hasattr(self.platform, 'name'):
            self.state.platform_name = self.platform.name

    async def produce_content(self,
                            category: str,
                            style: Optional[str] = None,
                            article: Optional[Article] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            style: 写作风格
            article: 文章对象（可选）

        Returns:
            Dict: 生产结果
        """
        # 设置状态参数
        self.state.category = category
        self.state.style = style
        self.state.article = article

        # 阻止已发布文章的重新生成
        if article and article.is_published:
            raise ValueError("已发布文章不能重新生成")

        # 启动Flow
        result = await self.run()

        # 构建并返回结果
        production_result = {
            "timestamp": datetime.now().isoformat(),
            "final_output": self.state.final_output,
            "platform": self.state.platform_name,
            "status": self.state.status,
            "execution_time": self.state.execution_time,
            "delegated_tasks": self.state.delegated_tasks,
            "tasks_completed": self.state.tasks_completed
        }

        return production_result

    @start()
    def start_production(self):
        """开始内容生产流程"""
        logger.info(f"开始内容生产，类别: {self.state.category}，风格: {self.state.style}")

        # 更新状态
        self.state.mark_start()

        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_DISCOVERY, 1)

        return "内容生产启动成功"

    @listen(start_production)
    def execute_crew(self, _):
        """执行层级管理的Crew"""
        start_time = datetime.now()

        try:
            # 1. 创建专业Agent
            topic_advisor = self._create_topic_advisor()
            researcher = self._create_researcher()
            writer = self._create_writer()
            editor = self._create_editor()

            # 添加风格专家（如果需要风格处理）
            agents = [topic_advisor, researcher, writer, editor]
            if self.state.style:
                stylist = self._create_stylist()
                agents.append(stylist)

            # 2. 创建任务
            topic_task = self._create_topic_task(self.state.category)
            research_task = self._create_research_task()
            writing_task = self._create_writing_task(self.state.style)
            review_task = self._create_review_task()

            # 如果设置了风格，添加风格任务
            tasks = [topic_task, research_task, writing_task, review_task]
            if self.state.style:
                style_task = self._create_style_task()
                tasks.append(style_task)

            # 3. 创建带原生管理器的Crew
            content_crew = Crew(
                agents=agents,
                tasks=tasks,
                process=Process.hierarchical,  # 使用层级流程
                manager_llm=self.model_name,
                verbose=True
            )

            # 4. 启动Crew工作
            logger.info("启动CrewAI内容生产流程")
            result = content_crew.kickoff()

            # 5. 处理Crew结果
            if hasattr(result, 'raw'):
                # 保存最终结果
                self.state.final_output = result.raw
            else:
                self.state.final_output = str(result)

            # 处理任务执行结果
            if hasattr(result, 'tasks'):
                for task in result.tasks:
                    task_name = task.description.split('\n')[0].strip()
                    self.state.add_task_result(task_name, task.output)

            # 处理委派任务记录
            if hasattr(result, 'delegated_tasks'):
                for task in result.delegated_tasks:
                    self.state.add_delegated_task(task.description.split('\n')[0].strip())

            # 收集管理者的分析（如果有）
            if hasattr(result, 'manager_analysis'):
                self.state.manager_analysis = result.manager_analysis

            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.execution_time = execution_time

            logger.info(f"CrewAI内容生产完成，耗时: {execution_time:.2f}秒")

            # 保存到文章对象（如果有）
            if self.state.article and self.state.final_output:
                self.state.article.content = self.state.final_output
                from core.models.content_manager import ContentManager
                ContentManager.save_article(self.state.article)

            return "内容生产成功完成"

        except Exception as e:
            logger.error(f"CrewAI内容生产过程中出错: {str(e)}")
            self.state.mark_failed(str(e))
            self.current_progress.add_error(ProductionStage.ARTICLE_WRITING, str(e))
            return f"内容生产失败: {str(e)}"

    @listen(execute_crew)
    def complete_production(self, result):
        """完成内容生产"""
        if "失败" in result:
            self.state.mark_failed("执行过程中发生错误")
        else:
            self.state.mark_complete()

            # 更新所有阶段进度
            self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)
            self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)
            self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)
            self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)
            self.current_progress.complete_stage(ProductionStage.ARTICLE_REVIEW)

        return {
            "status": self.state.status,
            "execution_time": self.state.execution_time,
            "result": self.state.final_output
        }

    @listen(complete_production)
    def save_results(self, _):
        """保存结果并记录完成状态"""
        # 如果有文章对象，确保保存最终结果
        if self.state.article and self.state.final_output:
            try:
                from core.models.content_manager import ContentManager
                self.state.article.content = self.state.final_output
                self.state.article.status = "completed"
                self.state.article.completed_at = self.state.completed_at
                ContentManager.save_article(self.state.article)
                logger.info(f"文章内容已保存，ID: {self.state.article.id}")
            except Exception as e:
                logger.error(f"保存文章时出错: {str(e)}")

        return {
            "status": self.state.status,
            "message": "内容生产流程已完成",
            "has_article": self.state.article is not None
        }

    def _create_topic_advisor(self) -> Agent:
        """创建选题顾问Agent"""
        return Agent(
            role="Topic Advisor",
            goal="发现高质量的内容选题",
            backstory="你是一位资深内容策划师，精通分析热点趋势，能准确把握读者兴趣。",
            verbose=True,
            allow_delegation=True,
            llm=self.model_name
        )

    def _create_researcher(self) -> Agent:
        """创建研究员Agent"""
        return Agent(
            role="Content Researcher",
            goal="收集内容创作所需的全面且准确的资料",
            backstory="你是一位经验丰富的研究员，擅长深入调查各种主题，收集关键信息，分析数据并整理成有用的研究报告。",
            verbose=True,
            allow_delegation=True,
            llm=self.model_name
        )

    def _create_writer(self) -> Agent:
        """创建作家Agent"""
        return Agent(
            role="Content Writer",
            goal="创作高质量、引人入胜的内容",
            backstory="你是一位才华横溢的专业作家，擅长将复杂概念转化为引人入胜的内容，能够针对不同受众调整写作风格。",
            verbose=True,
            allow_delegation=True,
            llm=self.model_name
        )

    def _create_editor(self) -> Agent:
        """创建编辑Agent"""
        return Agent(
            role="Content Editor",
            goal="确保内容质量、准确性和风格一致性",
            backstory="你是一位细致入微的内容编辑，有着敏锐的文字感知能力，能发现并改进内容中的问题，确保最终输出的质量。",
            verbose=True,
            allow_delegation=True,
            llm=self.model_name
        )

    def _create_topic_task(self, category: str) -> Task:
        """创建选题任务"""
        return Task(
            description=f"""
            请基于当前热搜趋势，为类别'{category}'生成3个高质量的内容选题建议。

            对每个选题，提供：
            1. 选题标题
            2. 核心观点
            3. 预期受众
            4. 推荐理由
            5. 热度评分（1-10）

            最后，从中选择一个最佳选题，提供详细说明为何选择它。将最佳选题信息以JSON格式输出。
            """,
            expected_output="""
            JSON格式的最佳选题，包含title, core_points, target_audience, reason, score字段
            """,
            agent=self._create_topic_advisor()
        )

    def _create_research_task(self) -> Task:
        """创建研究任务"""
        return Task(
            description="""
            基于前一任务提供的选题，进行深入研究，收集以下内容：

            1. 背景信息：提供选题的历史背景和现状
            2. 关键数据：收集与选题相关的重要数据和统计信息
            3. 专家观点：汇总相关领域专家的见解
            4. 正反观点：收集不同立场的观点和论据
            5. 案例分析：提供2-3个相关案例

            将研究结果整理成结构化报告，以便写作团队使用。
            """,
            expected_output="""
            包含背景信息、关键数据、专家观点、正反观点和案例分析的结构化研究报告
            """,
            agent=self._create_researcher(),
            context=[self._create_topic_task]
        )

    def _create_writing_task(self, style: Optional[str] = None) -> Task:
        """创建写作任务

        Args:
            style: 可选参数，但写作阶段不关注风格
        """
        # 平台信息作为辅助约束（不涉及风格）
        platform_info = ""
        if hasattr(self, 'platform') and self.platform and hasattr(self.platform, 'name') and self.platform.name != "default":
            platform_info = f"注意考虑{self.platform.name}平台的目标受众特点。"

        # 从文章元数据中提取content_type，如果有的话
        content_type_info = ""
        if self.state.article and hasattr(self.state.article, 'content_type'):
            content_type_info = f"按照'{self.state.article.content_type}'内容类型的标准进行创作。"
        elif hasattr(self.state, 'content_type') and self.state.content_type:
            content_type_info = f"按照'{self.state.content_type}'内容类型的标准进行创作。"

        return Task(
            description=f"""
            基于提供的研究资料，创作一篇原创、全面且有深度的文章。{content_type_info}

            内容创作要求：
            - 专注于内容质量和信息准确性
            - 逻辑结构清晰，论点有力
            - 确保内容原创，观点独到
            - 根据主题选择最合适的组织方式

            {platform_info}

            文章应当包含：
            - 引人注目的标题
            - 简洁明了的导言，点明主题
            - 组织合理的正文，包含研究中的关键信息
            - 适当的小标题划分段落
            - 总结性的结论，对主要观点进行回顾

            确保内容准确、清晰、连贯；论点有力，逻辑清晰；保持读者阅读兴趣。

            注意：在此阶段不需要特别关注风格问题，风格调整将在后续阶段处理。
            """,
            expected_output="""
            一篇完整的文章，包含标题、导言、正文和结论。
            """,
            agent=self._create_writer(),
            context=[self._create_research_task]
        )

    def _create_review_task(self) -> Task:
        """创建审核任务"""
        context_tasks = [self._create_writing_task]
        if hasattr(self.state, 'style') and self.state.style:
            context_tasks.append(self._create_style_task)

        return Task(
            description="""
            对前一任务完成的文章进行全面审核，评估以下方面：

            1. 内容质量：信息准确性、论证逻辑性、表达清晰度
            2. 结构组织：整体结构是否合理，各部分是否衔接紧密
            3. 语言表达：语言是否流畅，用词是否准确
            4. 受众匹配：内容是否符合目标受众期望
            5. 原创性与价值：内容是否有足够的原创见解和价值

            提供详细的审核报告，包括评分和改进建议。如有必要，直接修改文章内容。

            最后，输出修改后的最终文章。
            """,
            expected_output="""
            详细的审核报告（含评分和建议）以及修改后的最终文章
            """,
            agent=self._create_editor(),
            context=context_tasks
        )

    def _create_style_task(self) -> Task:
        """创建风格调整任务"""
        # 从状态中获取style
        style = self.state.style or "default"

        # 平台信息作为可选辅助约束
        platform_info = ""
        if hasattr(self, 'platform') and self.platform and hasattr(self.platform, 'name') and self.platform.name != "default":
            platform_info = f"，同时考虑{self.platform.name}平台的特定要求"

        return Task(
            description=f"""
            对前一任务完成的文章进行风格调整，使其符合"{style}"风格{platform_info}。

            需要调整的方面：
            1. 语言风格：根据"{style}"风格调整语气和表达方式
            2. 结构优化：根据"{style}"风格优化段落结构和层级关系
            3. 标题修饰：使标题更符合"{style}"风格的特点
            4. 开场调整：确保开场方式符合"{style}"风格
            5. 结尾优化：根据"{style}"风格优化结尾

            确保保留原文的核心信息和主要观点，同时增强文章的可读性和吸引力。
            """,
            expected_output="""
            风格调整后的完整文章，包含修改后的标题、导言、正文和结论
            """,
            agent=self._create_stylist(),
            context=[self._create_writing_task]
        )

    def _create_stylist(self) -> Agent:
        """创建风格专家Agent"""
        return Agent(
            role="Style Specialist",
            goal="优化内容风格，确保符合目标风格和受众需求",
            backstory="你是一位精通各种写作风格的专家，能够恰当调整内容的语调、格式和结构，增强内容表现力。",
            verbose=True,
            allow_delegation=True,
            llm=self.model_name
        )

    def get_state(self) -> Dict:
        """获取当前状态

        Returns:
            Dict: 当前状态信息
        """
        return self.state.dict()

    def get_progress(self) -> Dict:
        """获取进度信息

        Returns:
            Dict: 进度信息
        """
        progress = {
            "status": self.state.status,
            "current_stage": self.state.current_stage,
            "started_at": self.state.started_at.isoformat() if self.state.started_at else None,
            "completed_at": self.state.completed_at.isoformat() if self.state.completed_at else None,
            "execution_time": self.state.execution_time,
            "tasks_completed": self.state.tasks_completed,
            "delegated_tasks": self.state.delegated_tasks
        }

        if self.current_progress:
            progress["stages"] = self.current_progress.to_dict()

        return progress

    def cancel_production(self) -> Dict:
        """取消内容生产

        Returns:
            Dict: 取消结果
        """
        self.state.mark_cancelled()
        return {"status": "cancelled", "message": "内容生产已取消"}
