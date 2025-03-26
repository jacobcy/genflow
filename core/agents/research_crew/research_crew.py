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
from core.constants.content_types import (
    get_research_config,
    DEFAULT_RESEARCH_CONFIG,
    RESEARCH_CONFIG,
    RESEARCH_DEPTH_LIGHT,
    RESEARCH_DEPTH_MEDIUM,
    RESEARCH_DEPTH_DEEP
)

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

        # 使用统一的配置
        self.content_type_config = RESEARCH_CONFIG

        # 默认内容类型配置
        self.default_research_config = DEFAULT_RESEARCH_CONFIG.copy()

        # 当前研究配置
        self.current_research_config = self.default_research_config.copy()

    def _create_background_research_task(self, topic: str, content_type: Optional[str] = None) -> Task:
        """创建背景研究任务

        Args:
            topic: 研究话题
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）

        Returns:
            Task: 背景研究任务
        """
        logger.info(f"创建背景研究任务，话题: {topic}，内容类型: {content_type or '未指定'}")

        # 使用统一配置获取研究配置
        self.current_research_config = get_research_config(content_type)

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 根据研究深度调整任务描述
        depth_instructions = {
            "low": "进行快速但全面的背景调查，重点关注最基本的信息和关键事实。不需要深入历史发展和复杂概念解释。",
            "medium": "进行标准深度的背景研究，平衡全面性和深度，包括基本历史背景和主要概念解释。",
            "high": "进行深入全面的背景研究，详细探索历史发展、相关理论基础，并提供全面的概念解释和最新研究进展。"
        }

        # 构建任务描述
        description = f"""
            你正在研究话题: {topic}。请记住保持客观中立的立场，关注事实而非观点。这是{content_type or '一般'}类型的内容研究，请保持适当的专业深度。

            对话题"{topic}"进行{depth_instructions[depth_level]}

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
            """

        # 根据研究深度调整预期输出长度
        expected_outputs = {
            "low": "一份基础的背景研究报告，简明扼要，包含指定的所有部分，约800字",
            "medium": "一份详尽的背景研究报告，包含指定的所有部分，不少于1500字",
            "high": "一份深入的背景研究报告，包含指定的所有部分，词汇准确专业，不少于2500字，引用专业资料"
        }

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["background_researcher"]
        )

    def _create_expert_finder_task(self, topic: str, background_research: TaskOutput, content_type: Optional[str] = None) -> Task:
        """创建专家发现任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果
            content_type: 内容类型

        Returns:
            Task: 专家发现任务
        """
        logger.info(f"创建专家发现任务，话题: {topic}，内容类型: {content_type or '未指定'}")

        # 使用统一配置获取研究配置（如果已经设置则复用）
        if content_type:
            self.current_research_config = get_research_config(content_type)

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 构建任务描述，根据深度调整专家数量和分析深度
        expert_counts = {
            "low": "2-3位",
            "medium": "3-5位",
            "high": "5-7位"
        }

        description = f"""
            你正在寻找话题'{topic}'的专家观点。请确保收集多元观点，不要只关注单一立场的专家。这是{content_type or '一般'}类型的内容研究，请保持适当的专业深度。

            这是话题的背景研究报告，请参考以便更准确地找到相关专家:

            {background_research.raw_output}

            为话题"{topic}"寻找并分析领域专家的观点和见解。

            你的任务是:
            1. 识别该话题领域的{expert_counts[depth_level]}权威专家
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
            """

        # 根据研究深度调整预期输出长度
        expected_outputs = {
            "low": "一份简明的专家观点分析报告，包含指定的所有部分，约700字",
            "medium": "一份专家观点分析报告，包含指定的所有部分，不少于1200字",
            "high": "一份深入的专家观点分析报告，包含指定的所有部分，不少于2000字，引用详细的专家言论和出处"
        }

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["expert_finder"]
        )

    def _create_data_analysis_task(self, topic: str, background_research: TaskOutput, content_type: Optional[str] = None) -> Task:
        """创建数据分析任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果
            content_type: 内容类型

        Returns:
            Task: 数据分析任务
        """
        logger.info(f"创建数据分析任务，话题: {topic}，内容类型: {content_type or '未指定'}")

        # 使用统一配置获取研究配置（如果已经设置则复用）
        if content_type:
            self.current_research_config = get_research_config(content_type)

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 根据研究深度调整任务描述
        data_requirements = {
            "low": "收集基本统计数据和关键趋势，不需要深入分析",
            "medium": "收集足够的数据点，包括趋势分析和简单预测",
            "high": "进行全面深入的数据收集和分析，包括详细的统计分析和多维度比较"
        }

        description = f"""
            你正在分析话题'{topic}'的相关数据。要保持客观，避免过度解读数据。这是{content_type or '一般'}类型的内容研究，请保持适当的专业深度。

            这是话题的背景研究报告，请参考以确保你的数据分析与背景一致:

            {background_research.raw_output}

            对话题"{topic}"进行数据分析，{data_requirements[depth_level]}。

            你的任务是:
            1. 收集与该话题相关的关键数据和统计信息
            2. 分析数据中的模式、趋势和关联
            3. 比较不同来源和时间点的数据
            4. 评估数据的可靠性和代表性
            5. 提取对研究最有价值的数据洞见

            参考背景研究报告以确保你的数据分析与话题背景一致。

            输出应为一份数据分析报告，包含以下部分:
            - 关键数据点概述
            - 趋势和模式分析
            - 数据来源和可靠性评估
            - 数据的限制和不确定性
            - 数据支持的主要发现
            - 可视化建议(如适用)

            确保引用数据来源并说明数据收集的时间范围。
            """

        # 根据研究深度调整预期输出长度
        expected_outputs = {
            "low": "一份简明的数据分析报告，包含指定的所有部分，约600字",
            "medium": "一份详细的数据分析报告，包含指定的所有部分，不少于1000字",
            "high": "一份深入的数据分析报告，包含指定的所有部分，不少于1800字，包含详细的统计分析和数据解释"
        }

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["data_analyst"]
        )

    def _create_research_report_task(
        self,
        topic: str,
        background_research: TaskOutput,
        expert_insights: Optional[TaskOutput] = None,
        data_analysis: Optional[TaskOutput] = None,
        content_type: Optional[str] = None
    ) -> Task:
        """创建研究报告任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果
            expert_insights: 专家观点结果
            data_analysis: 数据分析结果
            content_type: 内容类型

        Returns:
            Task: 研究报告任务
        """
        logger.info(f"创建研究报告任务，话题: {topic}，内容类型: {content_type or '未指定'}")

        # 使用统一配置获取研究配置（如果已经设置则复用）
        if content_type:
            self.current_research_config = get_research_config(content_type)

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 整合所有研究结果
        description_parts = [
            f"你正在为话题'{topic}'撰写最终研究报告。这是{content_type or '一般'}类型的内容研究，请保持适当的专业深度。",
            "\n\n这是话题的背景研究报告:\n\n" + background_research.raw_output
        ]

        # 添加专家观点结果（如果有）
        if expert_insights:
            description_parts.append("\n\n这是相关专家的观点分析:\n\n" + expert_insights.raw_output)
        else:
            description_parts.append("\n\n没有专家观点分析数据。")

        # 添加数据分析结果（如果有）
        if data_analysis:
            description_parts.append("\n\n这是相关数据分析:\n\n" + data_analysis.raw_output)
        else:
            description_parts.append("\n\n没有数据分析结果。")

        # 报告要求
        report_requirements = {
            "low": "简明扼要的概述，重点关注最关键的信息，不需要深入分析",
            "medium": "全面但重点突出的报告，平衡详细程度和可读性",
            "high": "深入详尽的研究报告，包括全面的分析、多角度观点和完整的参考资料"
        }

        # 构建任务描述
        task_description = f"""
            根据提供的背景研究、专家观点和数据分析，为话题"{topic}"撰写一份{report_requirements[depth_level]}。

            你的任务是:
            1. 综合所有研究结果，形成一份结构清晰的研究报告
            2. 确保准确表达背景信息、专家观点和数据分析的关键内容
            3. 分析不同信息来源之间的关联和矛盾
            4. 提出基于研究的合理结论和建议
            5. 明确指出研究的局限性和未来研究方向

            报告应包含以下部分:
            - 执行摘要：简明扼要地概述研究的主要发现和结论
            - 引言：介绍研究背景、目的和范围
            - 研究方法：简述获取信息的方法和来源
            - 主要发现：详细阐述研究的关键发现，整合背景信息、专家见解和数据分析
            - 讨论：分析发现的含义、局限性和与现有知识的关系
            - 结论和建议：总结主要观点并提出基于研究的建议
            - 参考资料：列出主要信息来源（如适用）

            确保报告专业、客观、结构清晰，内容深度符合{content_type or '一般'}类型内容的要求。
            """

        # 将所有部分组合到一个description中
        description_parts.append(task_description)
        description = "".join(description_parts)

        # 根据研究深度调整预期输出长度
        expected_outputs = {
            "low": "一份简明的研究报告，包含指定的所有部分，约1500字",
            "medium": "一份全面的研究报告，包含指定的所有部分，不少于2500字",
            "high": "一份深入详尽的研究报告，包含指定的所有部分，不少于4000字，专业术语准确，分析深入"
        }

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["research_writer"]
        )

    async def research_topic(self, topic: str, content_type: Optional[str] = None, progress_callback=None) -> ResearchResult:
        """执行话题研究流程

        这是研究团队的主要工作流程，按以下步骤执行：
        1. 背景研究：收集话题的基础信息和背景知识
        2. 专家发现：寻找并分析相关领域专家的观点和见解
        3. 数据分析：分析与话题相关的数据和趋势
        4. 研究报告生成：整合前三步的结果，生成完整的研究报告

        Args:
            topic: 要研究的话题
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）
            progress_callback: 可选的进度回调函数，接收阶段名称和完成百分比参数

        Returns:
            ResearchResult: 研究结果对象
        """
        logger.info(f"开始研究话题: {topic}, 内容类型: {content_type or '未指定'}")

        # 使用统一配置获取研究配置
        self.current_research_config = get_research_config(content_type)
        logger.info(f"研究配置: {self.current_research_config}")

        # 创建工作流结果跟踪对象
        workflow_result = ResearchWorkflowResult(topic=topic)
        self.last_workflow_result = workflow_result

        # 根据内容类型配置决定是否需要专家和数据分析
        needs_expert = self.current_research_config["needs_expert"]
        needs_data_analysis = self.current_research_config["needs_data_analysis"]

        try:
            # 第1步：背景研究 (始终执行)
            if progress_callback:
                progress_callback("背景研究", 0.0)

            background_task = self._create_background_research_task(topic, content_type)

            # 使用单智能体执行任务
            logger.info("执行背景研究任务...")
            background_crew = Crew(
                agents=[self.agents["background_researcher"]],
                tasks=[background_task],
                verbose=True
            )
            background_result = background_crew.kickoff()
            workflow_result.background_research = background_result[0]

            if progress_callback:
                progress_callback("背景研究", 1.0)

            # 第2步：专家观点研究（可选）
            expert_result = None
            if needs_expert:
                if progress_callback:
                    progress_callback("专家观点研究", 0.0)

                expert_task = self._create_expert_finder_task(
                    topic, background_result[0], content_type
                )

                # 使用单智能体执行任务
                logger.info("执行专家观点研究任务...")
                expert_crew = Crew(
                    agents=[self.agents["expert_finder"]],
                    tasks=[expert_task],
                    verbose=True
                )
                expert_result = expert_crew.kickoff()
                workflow_result.expert_insights = expert_result[0]

                if progress_callback:
                    progress_callback("专家观点研究", 1.0)
            else:
                logger.info(f"根据内容类型'{content_type}'配置，跳过专家观点研究")

            # 第3步：数据分析（可选）
            data_analysis_result = None
            if needs_data_analysis:
                if progress_callback:
                    progress_callback("数据分析", 0.0)

                data_task = self._create_data_analysis_task(
                    topic, background_result[0], content_type
                )

                # 使用单智能体执行任务
                logger.info("执行数据分析任务...")
                data_crew = Crew(
                    agents=[self.agents["data_analyst"]],
                    tasks=[data_task],
                    verbose=True
                )
                data_analysis_result = data_crew.kickoff()
                workflow_result.data_analysis = data_analysis_result[0]

                if progress_callback:
                    progress_callback("数据分析", 1.0)
            else:
                logger.info(f"根据内容类型'{content_type}'配置，跳过数据分析")

            # 第4步：生成最终研究报告（始终执行）
            if progress_callback:
                progress_callback("研究报告生成", 0.0)

            report_task = self._create_research_report_task(
                topic,
                background_result[0],
                expert_result[0] if expert_result else None,
                data_analysis_result[0] if data_analysis_result else None,
                content_type
            )

            # 使用单智能体执行任务
            logger.info("生成最终研究报告...")
            report_crew = Crew(
                agents=[self.agents["research_writer"]],
                tasks=[report_task],
                verbose=True
            )
            report_result = report_crew.kickoff()
            workflow_result.research_report = report_result[0]

            if progress_callback:
                progress_callback("研究报告生成", 1.0)

            # 处理最终结果
            logger.info("处理研究结果...")
            research_result = self._process_research_result(
                topic,
                report_result[0].raw_output,
                workflow_result
            )

            # 添加内容类型信息到元数据
            if not hasattr(research_result, "metadata"):
                research_result.metadata = {}
            research_result.metadata["content_type"] = content_type
            research_result.metadata["research_config"] = self.current_research_config.copy()

            # 存储最终结果
            workflow_result.result = research_result

            logger.info(f"话题'{topic}'研究完成")
            return research_result

        except Exception as e:
            logger.error(f"研究过程中出错: {e}")
            # 继续抛出异常以便上层处理
            raise

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

    def _process_research_result(
        self,
        topic: str,
        report: str,
        workflow_result: ResearchWorkflowResult
    ) -> ResearchResult:
        """处理研究结果，生成最终的ResearchResult对象

        Args:
            topic: 研究话题
            report: 研究报告内容
            workflow_result: 工作流结果对象

        Returns:
            ResearchResult: 处理后的研究结果对象
        """
        logger.info(f"处理研究结果，话题: {topic}")

        # 创建研究结果对象
        research_result = ResearchResult(
            topic=topic,
            summary=report,
            background=workflow_result.background_research.raw_output if workflow_result.background_research else "",
            expert_insights=workflow_result.expert_insights.raw_output if workflow_result.expert_insights else "",
            data_analysis=workflow_result.data_analysis.raw_output if workflow_result.data_analysis else "",
            report=report,
            metadata={
                "workflow_id": workflow_result.id,
                "created_at": datetime.now().isoformat()
            }
        )

        logger.info("研究结果处理完成")
        return research_result
