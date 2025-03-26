"""CrewAI Flow状态管理控制器

该模块使用CrewAI的Flow API实现内容生产流程的状态管理，
提供更结构化、可追踪的内容生产过程。
"""

import logging
import os
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Task, Crew, Process

from core.models.topic import Topic
from core.models.article import Article
from core.models.platform import Platform, get_default_platform
from core.models.progress import ProductionStage

logger = logging.getLogger(__name__)

class ContentProductionState(BaseModel):
    """内容生产状态模型

    使用Pydantic模型定义内容生产流程各阶段的状态和数据。
    """
    # 输入参数
    category: str = ""
    style: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    platform_name: str = "default"

    # 阶段状态和结果
    topic_started: bool = False
    topic_completed: bool = False
    topic_result: Dict = Field(default_factory=dict)

    research_started: bool = False
    research_completed: bool = False
    research_result: Dict = Field(default_factory=dict)

    writing_started: bool = False
    writing_completed: bool = False
    writing_result: Dict = Field(default_factory=dict)

    style_started: bool = False
    style_completed: bool = False
    style_result: Dict = Field(default_factory=dict)

    review_started: bool = False
    review_completed: bool = False
    review_result: Dict = Field(default_factory=dict)

    # 最终内容
    final_content: Optional[str] = None

    # 监控数据
    started_at: Optional[datetime] = None
    last_updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_stage: str = "initialized"  # initialized, topic, research, writing, style, review, completed, failed
    status: str = "pending"  # pending, running, completed, failed, cancelled
    error: Optional[str] = None

    # 执行统计
    execution_times: Dict[str, float] = Field(default_factory=dict)
    total_execution_time: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=dict)

    def mark_stage_start(self, stage: str):
        """标记阶段开始"""
        setattr(self, f"{stage}_started", True)
        self.current_stage = stage
        self.last_updated_at = datetime.now()

    def mark_stage_complete(self, stage: str, result: Dict):
        """标记阶段完成"""
        setattr(self, f"{stage}_completed", True)
        setattr(self, f"{stage}_result", result)
        self.last_updated_at = datetime.now()

    def add_execution_time(self, stage: str, seconds: float):
        """添加执行时间"""
        self.execution_times[stage] = seconds
        self.total_execution_time += seconds

    def add_token_usage(self, stage: str, tokens: int):
        """添加token使用量"""
        self.token_usage[stage] = tokens

    def get_progress(self) -> Dict:
        """获取进度信息"""
        stages = ["topic", "research", "writing", "style", "review"]
        progress = {}

        for stage in stages:
            progress[stage] = {
                "started": getattr(self, f"{stage}_started", False),
                "completed": getattr(self, f"{stage}_completed", False),
                "execution_time": self.execution_times.get(stage, 0)
            }

        progress["overall"] = {
            "status": self.status,
            "current_stage": self.current_stage,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_execution_time": self.total_execution_time,
            "error": self.error
        }

        return progress

class CrewAIFlowController(Flow[ContentProductionState]):
    """使用CrewAI Flow API的内容生产控制器

    通过CrewAI Flow提供状态管理功能，使内容生产流程更可靠、可追踪。
    每个生产阶段都有明确的状态跟踪，支持进度监控和错误处理。
    """

    def __init__(self, model_name="gpt-4"):
        """初始化Flow控制器

        Args:
            model_name: Agent使用的LLM模型名称
        """
        super().__init__()
        self.model_name = model_name
        self.platform = None

    async def initialize(self, platform: Optional[Platform] = None):
        """初始化控制器

        Args:
            platform: 目标平台，如果不提供则使用默认配置
        """
        self.platform = platform or get_default_platform()
        logger.info(f"CrewAI Flow控制器已初始化，使用模型: {self.model_name}")

        # 设置平台信息到状态
        if hasattr(self.state, 'platform_name') and hasattr(self.platform, 'name'):
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
        # 设置初始状态
        self.state.category = category
        self.state.style = style
        self.state.keywords = keywords or []

        # 启动Flow
        result = await self.run()

        # 返回最终结果
        return {
            "state": self.state.dict(),
            "content": self.state.final_content,
            "progress": self.state.get_progress(),
            "status": self.state.status
        }

    @start()
    def start_production(self):
        """开始内容生产流程"""
        logger.info(f"开始内容生产，类别: {self.state.category}，风格: {self.state.style}")

        # 更新状态
        self.state.started_at = datetime.now()
        self.state.last_updated_at = datetime.now()
        self.state.status = "running"

        return "内容生产启动成功"

    @listen(start_production)
    def discover_topic(self, _):
        """执行选题阶段"""
        start_time = datetime.now()

        try:
            # 更新状态
            self.state.mark_stage_start("topic")
            logger.info("开始选题阶段")

            # 创建Agent和Task
            topic_advisor = self._create_topic_advisor()
            topic_task = self._create_topic_task(
                self.state.category,
                self.state.keywords
            )

            # 创建Crew
            topic_crew = Crew(
                agents=[topic_advisor],
                tasks=[topic_task],
                verbose=True,
                llm=self.model_name
            )

            # 执行任务
            result = topic_crew.kickoff()

            # 处理结果
            result_dict = {
                "raw_output": result,
                "timestamp": datetime.now().isoformat()
            }

            # 更新状态
            self.state.mark_stage_complete("topic", result_dict)

            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.add_execution_time("topic", execution_time)

            logger.info(f"选题阶段完成，耗时: {execution_time:.2f}秒")
            return "选题阶段完成"

        except Exception as e:
            logger.error(f"选题阶段出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = f"选题阶段错误: {str(e)}"
            return f"选题阶段失败: {str(e)}"

    @listen(discover_topic)
    def research_topic(self, _):
        """执行研究阶段"""
        start_time = datetime.now()

        try:
            # 检查上一阶段是否成功
            if not self.state.topic_completed:
                self.state.status = "failed"
                self.state.error = "无法执行研究：选题阶段未完成"
                return "研究阶段失败：选题阶段未完成"

            # 更新状态
            self.state.mark_stage_start("research")
            logger.info("开始研究阶段")

            # 创建Agent和Task
            researcher = self._create_researcher()
            research_task = self._create_research_task()

            # 创建Crew
            research_crew = Crew(
                agents=[researcher],
                tasks=[research_task],
                verbose=True,
                llm=self.model_name
            )

            # 执行任务
            result = research_crew.kickoff()

            # 处理结果
            result_dict = {
                "raw_output": result,
                "timestamp": datetime.now().isoformat()
            }

            # 更新状态
            self.state.mark_stage_complete("research", result_dict)

            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.add_execution_time("research", execution_time)

            logger.info(f"研究阶段完成，耗时: {execution_time:.2f}秒")
            return "研究阶段完成"

        except Exception as e:
            logger.error(f"研究阶段出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = f"研究阶段错误: {str(e)}"
            return f"研究阶段失败: {str(e)}"

    @listen(research_topic)
    def write_content(self, _):
        """执行写作阶段"""
        start_time = datetime.now()

        try:
            # 检查上一阶段是否成功
            if not self.state.research_completed:
                self.state.status = "failed"
                self.state.error = "无法执行写作：研究阶段未完成"
                return "写作阶段失败：研究阶段未完成"

            # 更新状态
            self.state.mark_stage_start("writing")
            logger.info("开始写作阶段")

            # 创建Agent和Task
            writer = self._create_writer()
            writing_task = self._create_writing_task(self.state.style)

            # 创建Crew
            writing_crew = Crew(
                agents=[writer],
                tasks=[writing_task],
                verbose=True,
                llm=self.model_name
            )

            # 执行任务
            result = writing_crew.kickoff()

            # 处理结果
            result_dict = {
                "raw_output": result,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": datetime.now().isoformat()
            }

            # 更新状态
            self.state.mark_stage_complete("writing", result_dict)

            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.add_execution_time("writing", execution_time)

            logger.info(f"写作阶段完成，耗时: {execution_time:.2f}秒")
            return "写作阶段完成"

        except Exception as e:
            logger.error(f"写作阶段出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = f"写作阶段错误: {str(e)}"
            return f"写作阶段失败: {str(e)}"

    @listen(write_content)
    def adapt_style(self, _):
        """执行风格调整阶段"""
        start_time = datetime.now()

        try:
            # 检查上一阶段是否成功
            if not self.state.writing_completed:
                self.state.status = "failed"
                self.state.error = "无法执行风格调整：写作阶段未完成"
                return "风格调整阶段失败：写作阶段未完成"

            # 更新状态
            self.state.mark_stage_start("style")
            logger.info("开始风格调整阶段")

            # 获取写作内容
            content = self.state.writing_result.get("content", "")

            # 创建Agent和Task
            stylist = self._create_stylist()
            style_task = self._create_style_task(content)

            # 创建Crew
            style_crew = Crew(
                agents=[stylist],
                tasks=[style_task],
                verbose=True,
                llm=self.model_name
            )

            # 执行任务
            result = style_crew.kickoff()

            # 处理结果
            result_dict = {
                "raw_output": result,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": datetime.now().isoformat()
            }

            # 更新状态
            self.state.mark_stage_complete("style", result_dict)

            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.add_execution_time("style", execution_time)

            logger.info(f"风格调整阶段完成，耗时: {execution_time:.2f}秒")
            return "风格调整阶段完成"

        except Exception as e:
            logger.error(f"风格调整阶段出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = f"风格调整阶段错误: {str(e)}"
            return f"风格调整阶段失败: {str(e)}"

    @listen(adapt_style)
    def review_content(self, _):
        """执行审核阶段"""
        start_time = datetime.now()

        try:
            # 检查上一阶段是否成功
            if not self.state.style_completed and not self.state.writing_completed:
                self.state.status = "failed"
                self.state.error = "无法执行审核：风格调整和写作阶段均未完成"
                return "审核阶段失败：无可用内容"

            # 更新状态
            self.state.mark_stage_start("review")
            logger.info("开始审核阶段")

            # 获取内容（优先使用风格调整后的内容）
            content = ""
            if self.state.style_completed:
                content = self.state.style_result.get("content", "")
            elif self.state.writing_completed:
                content = self.state.writing_result.get("content", "")

            # 创建Agent和Task
            editor = self._create_editor()
            review_task = self._create_review_task(content)

            # 创建Crew
            review_crew = Crew(
                agents=[editor],
                tasks=[review_task],
                verbose=True,
                llm=self.model_name
            )

            # 执行任务
            result = review_crew.kickoff()

            # 处理结果
            result_dict = {
                "raw_output": result,
                "content": result if isinstance(result, str) else str(result),
                "timestamp": datetime.now().isoformat()
            }

            # 更新状态
            self.state.mark_stage_complete("review", result_dict)
            self.state.final_content = result_dict.get("content", "")

            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.state.add_execution_time("review", execution_time)

            logger.info(f"审核阶段完成，耗时: {execution_time:.2f}秒")
            return "审核阶段完成"

        except Exception as e:
            logger.error(f"审核阶段出错: {str(e)}")
            self.state.status = "failed"
            self.state.error = f"审核阶段错误: {str(e)}"
            return f"审核阶段失败: {str(e)}"

    @listen(review_content)
    def complete_production(self, _):
        """完成内容生产流程"""
        # 更新状态
        self.state.completed_at = datetime.now()
        self.state.last_updated_at = datetime.now()
        self.state.status = "completed"
        self.state.current_stage = "completed"

        # 总结执行时间
        total_time = (self.state.completed_at - self.state.started_at).total_seconds()
        logger.info(f"内容生产完成，总耗时: {total_time:.2f}秒")

        return {
            "message": "内容生产完成",
            "total_time": total_time,
            "status": self.state.status
        }

    def _create_topic_advisor(self) -> Agent:
        """创建选题顾问Agent"""
        return Agent(
            role="Topic Advisor",
            goal="发现高质量的内容选题",
            backstory="你是一位资深内容策划师，精通分析热点趋势，能准确把握读者兴趣。",
            verbose=True,
            allow_delegation=False,
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

    def _create_topic_task(self, category: str, keywords: Optional[List[str]]) -> Task:
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
            agent=self._create_topic_advisor()
        )

    def _create_research_task(self) -> Task:
        """创建研究任务"""
        # 从状态获取选题信息
        topic_info = self.state.topic_result.get("raw_output", "未知选题")

        return Task(
            description=f"""
            基于以下选题信息，进行深入研究，收集以下内容：

            {topic_info}

            需要研究的内容：
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
            agent=self._create_researcher()
        )

    def _create_writing_task(self, style: Optional[str]) -> Task:
        """创建写作任务"""
        # 从状态获取研究信息
        research_info = self.state.research_result.get("raw_output", "未找到研究资料")
        topic_info = self.state.topic_result.get("raw_output", "未知选题")

        style_guidance = f"按照'{style}'风格写作" if style else "使用吸引目标受众的合适风格"

        return Task(
            description=f"""
            基于以下选题和研究报告，创作一篇高质量的内容。{style_guidance}。

            选题信息:
            {topic_info}

            研究报告:
            {research_info}

            内容应包括：
            1. 引人入胜的标题
            2. 简洁有力的导言，点明主题
            3. 按逻辑结构组织的正文，包含研究中的关键信息
            4. 适当的小标题划分段落
            5. 结论部分总结观点并给出见解

            要求：
            - 确保内容准确、清晰、连贯
            - 使用恰当的论据支持观点
            - 保持读者阅读兴趣
            """,
            expected_output="""
            一篇完整的文章，包含标题、导言、结构化正文和结论
            """,
            agent=self._create_writer()
        )

    def _create_style_task(self, content: str) -> Task:
        """创建风格调整任务"""
        platform_name = self.state.platform_name or "未指定平台"
        style_name = self.state.style or "通用"

        return Task(
            description=f"""
            对以下文章进行风格调整，使其更符合{platform_name}平台的特点和{style_name}风格的需求：

            {content}

            需要调整的方面：
            1. 语言风格：根据平台特点调整语气和表达方式
            2. 结构优化：优化段落结构和层级关系
            3. 标题修饰：使标题更具吸引力和平台特色
            4. 开场调整：确保开场能够快速吸引读者
            5. 结尾优化：强化结尾的有效性和行动号召力

            确保保留原文的核心信息和主要观点，同时增强文章的可读性和吸引力。
            """,
            expected_output="""
            风格调整后的完整文章，包含修改后的标题、导言、正文和结论
            """,
            agent=self._create_stylist()
        )

    def _create_review_task(self, content: str) -> Task:
        """创建审核任务"""
        return Task(
            description=f"""
            对以下文章进行全面审核，评估以下方面：

            {content}

            评估内容:
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
            agent=self._create_editor()
        )

# 使用示例
async def main():
    """主函数"""
    try:
        # 创建Flow控制器
        controller = CrewAIFlowController(model_name="gpt-4")

        # 初始化控制器
        await controller.initialize()

        # 生产内容
        result = await controller.produce_content(
            category="人工智能",
            style="科技",
            keywords=["大模型", "应用"]
        )

        # 打印结果
        print(f"内容生产完成，状态: {result['status']}")
        print(f"总执行时间: {result['progress']['overall']['total_execution_time']:.2f}秒")

    except Exception as e:
        print(f"内容生产失败: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
