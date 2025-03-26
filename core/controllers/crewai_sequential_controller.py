"""CrewAI标准顺序流程控制器

该模块使用CrewAI的Sequential Process实现内容生产流程，
确保任务按顺序依次执行，前一任务的输出作为后续任务的输入。
集成Flow API实现完整的状态管理。
"""

import logging
import os
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, listen, start

from core.models.topic import Topic
from core.models.article import Article
from core.models.platform import Platform, get_default_platform
from core.models.progress import ProductionProgress, ProductionStage

logger = logging.getLogger(__name__)

class SequentialProductionState(BaseModel):
    """顺序流程内容生产状态模型"""
    # 输入参数
    category: str = ""
    style: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    platform_name: str = "default"

    # 任务结果
    topic_result: Optional[Any] = None
    research_result: Optional[Any] = None
    writing_result: Optional[Any] = None
    style_result: Optional[Any] = None
    review_result: Optional[Any] = None

    # 任务执行状态
    tasks_completed: List[str] = Field(default_factory=list)
    tasks_output: Dict[str, Any] = Field(default_factory=dict)

    # 生产结果
    final_output: Optional[Any] = None

    # 监控数据
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_stage: str = "initialized"  # initialized, running, completed, failed
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None

    # 执行统计
    execution_time: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)

class CrewAISequentialController(Flow[SequentialProductionState]):
    """使用CrewAI标准顺序流程的内容生产控制器

    通过CrewAI的Sequential Process实现内容生产各阶段的顺序执行。
    每个阶段由专业Agent完成特定任务，前一阶段的结果传递给下一阶段。
    集成Flow API实现状态管理。
    """

    def __init__(self, model_name="gpt-4"):
        """初始化顺序流程控制器

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
        logger.info(f"CrewAI顺序流程控制器已初始化，使用模型: {self.model_name}")
        self.current_progress = ProductionProgress()

        # 设置平台信息到状态
        if hasattr(self.platform, 'name'):
            self.state.platform_name = self.platform.name

    async def produce_content(self,
                            category: str,
                            style: Optional[str] = None,
                            keywords: Optional[List[str]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            style: 写作风格
            keywords: 关键词列表

        Returns:
            Dict: 生产结果
        """
        # 设置状态参数
        self.state.category = category
        self.state.style = style
        self.state.keywords = keywords or []

        # 启动Flow
        result = await self.run()

        # 构建并返回结果
        production_result = {
            "timestamp": datetime.now().isoformat(),
            "tasks_output": self.state.tasks_output,
            "final_output": self.state.final_output,
            "platform": self.state.platform_name,
            "status": self.state.status,
            "execution_time": self.state.execution_time
        }

        return production_result

    @start()
    def start_production(self):
        """开始内容生产流程"""
        logger.info(f"开始内容生产，类别: {self.state.category}，风格: {self.state.style}")

        # 更新状态
        self.state.started_at = datetime.now()
        self.state.status = "running"
        self.state.current_stage = "running"

        # 更新进度
        self.current_progress.start_stage(ProductionStage.TOPIC_DISCOVERY, 1)

        return "内容生产启动成功"

    @listen(start_production)
    def execute_sequential_crew(self, _):
        """执行顺序流程Crew"""
        start_time = datetime.now()

        try:
            # 1. 创建专业Agent
            topic_advisor = self._create_topic_advisor()
            researcher = self._create_researcher()
            writer = self._create_writer()
            stylist = self._create_stylist()
            editor = self._create_editor()

            # 2. 创建顺序任务
            topic_task = self._create_topic_task(self.state.category, self.state.keywords, topic_advisor)
            research_task = self._create_research_task(researcher)
            writing_task = self._create_writing_task(self.state.style, writer)
            style_task = self._create_style_task(stylist)
            review_task = self._create_review_task(editor)

            # 3. 创建顺序流程Crew
            content_crew = Crew(
                agents=[topic_advisor, researcher, writer, stylist, editor],
                tasks=[topic_task, research_task, writing_task, style_task, review_task],
                process=Process.sequential,  # 使用顺序流程
                verbose=True,
                llm=self.model_name
            )

            # 4. 启动Crew工作
            logger.info("启动CrewAI顺序内容生产流程")
            result = content_crew.kickoff()

            # 5. 处理结果
            self._process_crew_result(result)

            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.execution_time = execution_time

            logger.info(f"CrewAI顺序内容生产完成，耗时: {execution_time:.2f}秒")

            # 更新所有阶段进度
            self.current_progress.complete_stage(ProductionStage.TOPIC_DISCOVERY)
            self.current_progress.complete_stage(ProductionStage.TOPIC_RESEARCH)
            self.current_progress.complete_stage(ProductionStage.ARTICLE_WRITING)
            self.current_progress.complete_stage(ProductionStage.STYLE_ADAPTATION)
            self.current_progress.complete_stage(ProductionStage.ARTICLE_REVIEW)

            return "内容生产成功完成"

        except Exception as e:
            logger.error(f"CrewAI顺序内容生产过程中出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = str(e)
            self.current_progress.add_error(ProductionStage.ARTICLE_WRITING, str(e))
            return f"内容生产失败: {str(e)}"

    @listen(execute_sequential_crew)
    def complete_production(self, result):
        """完成内容生产"""
        if "失败" in result:
            self.state.status = "failed"
            self.state.current_stage = "failed"
        else:
            self.state.status = "completed"
            self.state.current_stage = "completed"
            self.state.completed_at = datetime.now()

        return {
            "status": self.state.status,
            "execution_time": self.state.execution_time,
            "tasks_count": len(self.state.tasks_completed)
        }

    def _process_crew_result(self, result: Any):
        """处理Crew执行结果

        Args:
            result: CrewAI执行结果对象
        """
        # 处理任务输出
        if hasattr(result, 'tasks'):
            for i, task in enumerate(result.tasks):
                stage_name = [
                    "topic_discovery",
                    "research",
                    "writing",
                    "style_adaptation",
                    "review"
                ][i if i < 5 else 4]

                self.state.tasks_output[stage_name] = task.output
                self.state.tasks_completed.append(stage_name)

        # 处理最终输出
        if hasattr(result, 'output'):
            self.state.final_output = result.output
        else:
            self.state.final_output = "任务完成，但无最终输出数据"

    def _create_topic_advisor(self) -> Agent:
        """创建选题顾问Agent"""
        return Agent(
            role="Topic Advisor",
            goal="发现高质量的内容选题",
            backstory="你是一位资深内容策划师，精通分析热点趋势，能准确把握读者兴趣。",
            verbose=True,
            allow_delegation=False,  # 顺序流程中关闭委派
            llm=self.model_name
        )

    def _create_researcher(self) -> Agent:
        """创建研究员Agent"""
        return Agent(
            role="Content Researcher",
            goal="收集内容创作所需的全面且准确的资料",
            backstory="你是一位经验丰富的研究员，擅长深入调查各种主题，收集关键信息，分析数据并整理成有用的研究报告。",
            verbose=True,
            allow_delegation=False,
            llm=self.model_name
        )

    def _create_writer(self) -> Agent:
        """创建作家Agent"""
        return Agent(
            role="Content Writer",
            goal="创作高质量、引人入胜的内容",
            backstory="你是一位才华横溢的专业作家，擅长将复杂概念转化为引人入胜的内容，能够针对不同受众调整写作风格。",
            verbose=True,
            allow_delegation=False,
            llm=self.model_name
        )

    def _create_stylist(self) -> Agent:
        """创建风格师Agent"""
        return Agent(
            role="Style Specialist",
            goal="优化内容风格，确保符合目标平台和受众需求",
            backstory="你是一位精通各种写作风格和平台要求的专家，能够恰当调整内容的语调、格式和结构，增强内容表现力。",
            verbose=True,
            allow_delegation=False,
            llm=self.model_name
        )

    def _create_editor(self) -> Agent:
        """创建编辑Agent"""
        return Agent(
            role="Content Editor",
            goal="确保内容质量、准确性和风格一致性",
            backstory="你是一位细致入微的内容编辑，有着敏锐的文字感知能力，能发现并改进内容中的问题，确保最终输出的质量。",
            verbose=True,
            allow_delegation=False,
            llm=self.model_name
        )

    def _create_topic_task(self, category: str, keywords: Optional[List[str]], agent: Agent) -> Task:
        """创建选题任务"""
        keywords_text = f"关键词：{', '.join(keywords)}" if keywords else ""
        return Task(
            description=f"""
            请基于当前热搜趋势，为类别'{category}'生成3个高质量的内容选题建议。{keywords_text}

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
            agent=agent  # 在顺序流程中必须直接指定agent
        )

    def _create_research_task(self, agent: Agent) -> Task:
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
            agent=agent
        )

    def _create_writing_task(self, content_type: Optional[str] = None, agent: Agent = None) -> Task:
        """创建写作任务

        Args:
            content_type: 内容类型，如"新闻"、"博客"等
            agent: 写作Agent
        """
        # 内容类型指导
        content_type_info = f"遵循'{content_type}'内容类型的标准结构" if content_type else "使用适合主题的内容结构"

        return Task(
            description=f"""
            基于研究报告提供的材料，创作一篇高质量的内容。{content_type_info}。

            内容创作要求：
            - 专注于内容质量和信息准确性
            - 逻辑结构清晰，论点有力
            - 确保内容原创，观点独到

            文章应包括：
            1. 引人入胜的标题
            2. 简洁有力的导言，点明主题
            3. 按逻辑结构组织的正文，包含研究中的关键信息
            4. 适当的小标题划分段落
            5. 结论部分总结观点并给出见解

            要求：
            - 确保内容准确、清晰、连贯
            - 使用恰当的论据支持观点
            - 保持读者阅读兴趣

            注意：在此阶段不需要特别关注风格问题，文章风格将在后续阶段调整。
            """,
            expected_output="""
            一篇完整的文章，包含标题、导言、结构化正文和结论
            """,
            agent=agent
        )

    def _create_style_task(self, stylist: Agent) -> Task:
        """创建风格调整任务"""
        # 从状态中获取style
        style = self.state.style or "default"

        # 平台信息作为可选辅助约束
        platform_info = ""
        if hasattr(self.platform, "name") and self.platform.name != "default":
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
            agent=stylist
        )

    def _create_review_task(self, agent: Agent) -> Task:
        """创建审核任务"""
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
            agent=agent
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
            "tasks_completed": self.state.tasks_completed
        }

        if self.current_progress:
            progress["stages"] = self.current_progress.to_dict()

        return progress


# 使用示例
async def main():
    """主函数"""
    try:
        # 创建顺序流程控制器
        controller = CrewAISequentialController()

        # 初始化控制器
        await controller.initialize()

        # 生产内容
        result = await controller.produce_content(
            category="技术",
            style="专业"
        )

        # 打印结果
        print(f"内容生产完成，状态: {result['status']}")

    except Exception as e:
        print(f"内容生产失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
