"""研究团队管理模块

这个模块定义了研究团队的组织和工作流程，负责协调各个研究智能体的工作，
完成从话题研究到生成研究报告的全流程。
"""
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import asyncio
import uuid

from crewai import Crew, Task, Agent
from crewai.tasks.task_output import TaskOutput
from core.models.article_outline import ArticleOutline
from core.models.basic_outline import OutlineSection
from core.models.research import BasicResearch, TopicResearch, ExpertInsight, KeyFinding, ArticleSection
from core.config import Config
from core.models.util.enums import ArticleSectionType
from core.agents.research_crew.research_agents import ResearchAgents
from core.models.feedback import ResearchFeedback

# 定义研究深度常量
RESEARCH_DEPTH_LIGHT = "light"
RESEARCH_DEPTH_MEDIUM = "medium"
RESEARCH_DEPTH_DEEP = "deep"

# 默认研究配置
DEFAULT_RESEARCH_CONFIG = {
    "content_type": "article",
    "depth": RESEARCH_DEPTH_MEDIUM,
    "needs_expert": True,
    "needs_data_analysis": True,
    "max_sources": 10
}

# 研究配置映射
RESEARCH_CONFIG = {
    "article": DEFAULT_RESEARCH_CONFIG,
    "blog": {
        "content_type": "blog",
        "depth": RESEARCH_DEPTH_MEDIUM,
        "needs_expert": True,
        "needs_data_analysis": False,
        "max_sources": 5
    },
    "news": {
        "content_type": "news",
        "depth": RESEARCH_DEPTH_LIGHT,
        "needs_expert": True,
        "needs_data_analysis": True,
        "max_sources": 3
    },
    "technical": {
        "content_type": "technical",
        "depth": RESEARCH_DEPTH_DEEP,
        "needs_expert": True,
        "needs_data_analysis": True,
        "max_sources": 15
    }
}

# 获取研究配置的辅助函数
def get_research_config(content_type=None):
    """获取指定内容类型的研究配置

    Args:
        content_type: 内容类型ID

    Returns:
        Dict: 研究配置
    """
    if not content_type:
        return DEFAULT_RESEARCH_CONFIG.copy()

    return RESEARCH_CONFIG.get(content_type, DEFAULT_RESEARCH_CONFIG).copy()

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
    topic_id: Optional[str] = None

    # 工作流执行结果
    background_research: Optional[TaskOutput] = None
    expert_insights: Optional[TaskOutput] = None
    data_analysis: Optional[TaskOutput] = None
    research_report: Optional[TaskOutput] = None

    # 最终研究结果
    result: Optional[BasicResearch] = None

    # 反馈信息
    feedback: Optional[ResearchFeedback] = None

    # 新添加的属性
    experts: List[str] = field(default_factory=list)
    research_results: str = ""

    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式

        Returns:
            Dict[str, Any]: 字典形式的结果
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "topic": self.topic,
            "topic_id": self.topic_id,
            "background_research": self.background_research.raw_output if self.background_research else None,
            "expert_insights": self.expert_insights.raw_output if self.expert_insights else None,
            "data_analysis": self.data_analysis.raw_output if self.data_analysis else None,
            "research_report": self.research_report.raw_output if self.research_report else None,
            "result": self.result.to_dict() if self.result else None,
            "feedback": self.feedback.to_dict() if self.feedback else None,
            "experts": self.experts,
            "research_results": self.research_results,
            "metadata": self.metadata
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

    def _create_background_research_task(self, topic: str) -> Task:
        """创建背景研究任务

        Args:
            topic: 研究话题

        Returns:
            Task: 背景研究任务
        """
        logger.info(f"创建背景研究任务，话题: {topic}")

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

        # 获取内容类型信息（如果有）
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 构建任务描述
        description = f"""
            你正在研究话题: {topic}。请记住保持客观中立的立场，关注事实而非观点。这是{content_type_display}类型的内容研究，请保持适当的专业深度。

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

    def _create_expert_finder_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建专家发现任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果

        Returns:
            Task: 专家发现任务
        """
        logger.info(f"创建专家发现任务，话题: {topic}")

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 获取内容类型信息（如果有）
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 构建任务描述，根据深度调整专家数量和分析深度
        expert_counts = {
            "low": "2-3位",
            "medium": "3-5位",
            "high": "5-7位"
        }

        description = f"""
            你正在寻找话题'{topic}'的专家观点。请确保收集多元观点，不要只关注单一立场的专家。这是{content_type_display}类型的内容研究，请保持适当的专业深度。

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

    def _create_data_analysis_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建数据分析任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果

        Returns:
            Task: 数据分析任务
        """
        logger.info(f"创建数据分析任务，话题: {topic}")

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 获取内容类型信息（如果有）
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 根据研究深度调整任务描述
        data_requirements = {
            "low": "收集基本统计数据和关键趋势，不需要深入分析",
            "medium": "收集足够的数据点，包括趋势分析和简单预测",
            "high": "进行全面深入的数据收集和分析，包括详细的统计分析和多维度比较"
        }

        description = f"""
            你正在分析话题'{topic}'的相关数据。要保持客观，避免过度解读数据。这是{content_type_display}类型的内容研究，请保持适当的专业深度。

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
        data_analysis: Optional[TaskOutput] = None
    ) -> Task:
        """创建研究报告任务

        Args:
            topic: 研究话题
            background_research: 背景研究结果
            expert_insights: 专家观点结果
            data_analysis: 数据分析结果

        Returns:
            Task: 研究报告任务
        """
        logger.info(f"创建研究报告任务，话题: {topic}")

        # 获取研究深度
        research_depth = self.current_research_config["depth"]
        depth_map = {
            RESEARCH_DEPTH_LIGHT: "low",
            RESEARCH_DEPTH_MEDIUM: "medium",
            RESEARCH_DEPTH_DEEP: "high"
        }
        depth_level = depth_map.get(research_depth, "medium")

        # 获取内容类型信息（如果有）
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 整合所有研究结果
        description_parts = [
            f"你正在为话题'{topic}'撰写最终研究报告。这是{content_type_display}类型的内容研究，请保持适当的专业深度。",
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

            确保报告专业、客观、结构清晰，内容深度符合{content_type_display}类型内容的要求。
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

    async def research_topic(
        self,
        topic: Union[str, Dict, Any],
        research_config: Optional[Dict[str, Any]] = None,
        depth: str = "medium",
        options: Optional[Dict[str, Any]] = None,
        progress_callback=None
    ) -> BasicResearch:
        """执行话题研究流程

        这是研究团队的主要工作流程，按以下步骤执行：
        1. 背景研究：收集话题的基础信息和背景知识
        2. 专家发现：寻找并分析相关领域专家的观点和见解
        3. 数据分析：分析与话题相关的数据和趋势
        4. 研究报告生成：整合前三步的结果，生成完整的研究报告

        注意：本方法不处理 content_type 的解析或 topic_id 映射逻辑，
        这些应该由上层 ResearchAdapter 完成。本方法只负责执行研究流程。

        Args:
            topic: 要研究的话题标题或描述(字符串或包含标题的对象)
            research_config: 研究配置，包含研究深度、是否需要专家和数据分析等
            depth: 研究深度（"shallow"/"medium"/"deep"）
            options: 附加选项，包含研究配置和元数据
            progress_callback: 可选的进度回调函数，接收阶段名称和完成百分比参数

        Returns:
            BasicResearch: 研究结果对象
        """
        # 处理不同类型的topic参数，提取标题
        topic_title = ""
        topic_id = None

        if isinstance(topic, str):
            topic_title = topic
            logger.info(f"开始研究话题: {topic_title}")
        else:
            # 假设是包含标题信息的对象
            topic_title = getattr(topic, 'title', str(topic))

            # 尝试获取话题ID（用于跟踪，但不影响研究逻辑）
            topic_id = getattr(topic, 'id', None)

            logger.info(f"开始研究话题: {topic_title}")

        # 设置研究配置
        if research_config:
            self.current_research_config = research_config
        else:
            # 使用默认研究配置
            self.current_research_config = DEFAULT_RESEARCH_CONFIG.copy()

        # 设置研究深度
        if depth == "shallow":
            research_depth = RESEARCH_DEPTH_LIGHT
        elif depth == "deep":
            research_depth = RESEARCH_DEPTH_DEEP
        else:
            research_depth = RESEARCH_DEPTH_MEDIUM

        # 更新研究配置中的深度
        self.current_research_config["depth"] = research_depth

        logger.info(f"研究配置: {self.current_research_config}")

        # 创建工作流结果跟踪对象
        workflow_result = ResearchWorkflowResult(topic=topic_title)
        self.last_workflow_result = workflow_result

        # 如果有话题ID，保存到工作流结果中（仅用于跟踪）
        if topic_id:
            workflow_result.topic_id = topic_id

        # 根据研究配置决定是否需要专家和数据分析
        needs_expert = self.current_research_config.get("needs_expert", True)
        needs_data_analysis = self.current_research_config.get("needs_data_analysis", True)

        try:
            # 第1步：背景研究 (始终执行)
            if progress_callback:
                progress_callback("背景研究", 0.0)

            background_task = self._create_background_research_task(topic_title)

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
                    topic_title, background_result[0]
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
                logger.info(f"根据研究配置，跳过专家观点研究")

            # 第3步：数据分析（可选）
            data_analysis_result = None
            if needs_data_analysis:
                if progress_callback:
                    progress_callback("数据分析", 0.0)

                data_task = self._create_data_analysis_task(
                    topic_title, background_result[0]
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
                logger.info(f"根据研究配置，跳过数据分析")

            # 第4步：生成最终研究报告（始终执行）
            if progress_callback:
                progress_callback("研究报告生成", 0.0)

            report_task = self._create_research_report_task(
                topic_title,
                background_result[0],
                expert_result[0] if expert_result else None,
                data_analysis_result[0] if data_analysis_result else None
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
            research_result = self._process_research_results(
                topic_title,
                workflow_result,
                workflow_result.background_research,
                workflow_result.expert_insights,
                workflow_result.data_analysis,
                workflow_result.research_report
            )

            # 确保研究配置中的深度正确
            if "research_config" not in research_result.metadata:
                research_result.metadata["research_config"] = {}
            research_result.metadata["research_config"]["depth"] = research_depth

            # 增加附加选项到元数据（如果有）
            if options:
                for key, value in options.items():
                    if key not in research_result.metadata:
                        research_result.metadata[key] = value

            # 存储最终结果
            workflow_result.result = research_result

            logger.info(f"话题'{topic_title}'研究完成")

            # 将ResearchWorkflowResult转换为BasicResearch返回
            return self._workflow_result_to_basic_research(research_result)

        except Exception as e:
            logger.error(f"研究过程中出错: {e}")
            # 继续抛出异常以便上层处理
            raise

    async def run_full_workflow(
        self,
        topic: Union[str, Dict, Any],
        research_config: Optional[Dict[str, Any]] = None,
        depth: str = "medium",
        options: Optional[Dict[str, Any]] = None,
        progress_callback=None
    ) -> BasicResearch:
        """运行完整的研究工作流程，不包含文章大纲生成

        Args:
            topic: 研究主题(字符串或Topic对象)
            research_config: 研究配置，包含研究深度、是否需要专家和数据分析等
            depth: 研究深度 ("shallow"/"medium"/"deep")
            options: 附加选项
            progress_callback: 进度回调函数

        Returns:
            BasicResearch: 研究结果
        """
        # 处理不同类型的topic参数
        topic_title = ""
        if isinstance(topic, str):
            topic_title = topic
        else:
            # 假设是Topic对象
            topic_title = getattr(topic, 'title', str(topic))

        logger.info(f"开始研究工作流，话题: {topic_title}")

        # 步骤: 研究话题
        if progress_callback:
            # 创建一个适配器函数，将research_topic的回调(name, progress)转换为
            # run_full_workflow的回调格式(step, total_steps, name)
            def callback_adapter(name, progress):
                # 进度基于research_topic的进度
                progress_callback(progress, 1.0, name)
        else:
            callback_adapter = None

        # 使用await关键字等待异步方法的结果
        research_result = await self.research_topic(
            topic,
            research_config=research_config,
            depth=depth,
            options=options,
            progress_callback=callback_adapter
        )

        logger.info(f"话题'{topic_title}'的研究工作流已完成")
        return research_result

    def get_human_feedback(self, result: BasicResearch) -> ResearchFeedback:
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

    def generate_article_outline(self, research_result: BasicResearch) -> ArticleOutline:
        """根据研究结果生成文章大纲

        Args:
            research_result: 研究结果

        Returns:
            ArticleOutline: 文章大纲对象
        """
        # 确保research_result有key_findings属性，并且是列表
        if not hasattr(research_result, 'key_findings') or research_result.key_findings is None:
            research_result.key_findings = []

        # 从研究结果中提取关键信息
        key_insights = [kf.content for kf in research_result.key_findings]

        # 创建文章大纲
        outline = ArticleOutline(
            title=f"{research_result.title}研究报告",
            summary=research_result.background or "",
            key_insights=key_insights,
            target_word_count=3000  # 设置默认目标字数
        )

        # 添加章节
        outline.sections = [
            OutlineSection(
                title="引言",
                content=research_result.background or "",
                order=1,
                section_type=ArticleSectionType.INTRODUCTION,
                key_points=["研究背景", "研究目的", "研究方法"]
            )
        ]

        # 添加主要发现章节
        main_sections = self._extract_main_sections_from_report(research_result.data_analysis or "")
        outline.sections.extend(main_sections)

        # 添加结论
        outline.sections.append(
            OutlineSection(
                title="结论",
                content="基于以上研究发现...",
                order=len(outline.sections) + 1,
                section_type=ArticleSectionType.CONCLUSION,
                key_points=key_insights[:3] if len(key_insights) >= 3 else key_insights  # 使用前3个关键发现作为结论要点
            )
        )

        return outline

    def _extract_main_sections_from_report(self, report: str) -> List[OutlineSection]:
        """从研究报告中提取主要章节

        Args:
            report: 研究报告文本

        Returns:
            List[OutlineSection]: 提取的文章章节列表
        """
        # 这里是一个简化的实现，实际应该使用更复杂的文本分析
        sections = []

        # 添加研究发现章节
        sections.append(
            OutlineSection(
                title="研究发现",
                content=report[:200] + "...",  # 使用报告开头作为内容预览
                order=2,
                section_type=ArticleSectionType.MAIN_POINT,
                key_points=["主要研究发现", "数据分析结果"]
            )
        )

        # 添加分析讨论章节
        sections.append(
            OutlineSection(
                title="分析讨论",
                content="基于研究发现进行深入分析...",
                order=3,
                section_type=ArticleSectionType.ANALYSIS,
                key_points=["发现解读", "影响分析", "未来展望"]
            )
        )

        return sections

    def _process_research_results(self, topic_title, workflow_result, background_research, expert_insights,
                             data_analysis, final_report):
        """处理研究结果，整合所有部分的结果

        Args:
            topic_title: 话题标题
            workflow_result: 工作流结果跟踪对象
            background_research: 背景研究结果
            expert_insights: 专家观点结果
            data_analysis: 数据分析结果
            final_report: 最终研究报告

        Returns:
            ResearchWorkflowResult: 处理后的研究结果
        """
        logger.info(f"处理研究结果，话题: {topic_title}")

        # 确保workflow_result有metadata属性
        if not hasattr(workflow_result, 'metadata') or workflow_result.metadata is None:
            workflow_result.metadata = {}

        # 将当前研究配置添加到元数据中
        if "research_config" not in workflow_result.metadata:
            workflow_result.metadata["research_config"] = self.current_research_config.copy()

        # 创建研究结果对象，保留原始的topic_id（如果有）
        result = ResearchWorkflowResult(
            topic=topic_title,
            topic_id=workflow_result.topic_id,  # 保留原始的topic_id
            background_research=background_research,
            expert_insights=expert_insights,
            data_analysis=data_analysis,
            research_report=final_report,
            metadata=workflow_result.metadata
        )

        # 处理专家见解
        if expert_insights and hasattr(expert_insights, 'raw_output'):
            try:
                expert_insights_text = expert_insights.raw_output
                result.experts = self._extract_experts_from_insights(expert_insights_text)
            except Exception as e:
                logger.error(f"提取专家见解时出错: {str(e)}")

        # 处理研究结果
        if final_report and hasattr(final_report, 'raw_output'):
            try:
                # 整合研究发现为最终结果
                result.research_results = final_report.raw_output
            except Exception as e:
                logger.error(f"处理研究报告时出错: {str(e)}")

        # 确保research_depth在metadata中被正确设置
        if "research_config" in result.metadata and "depth" in result.metadata["research_config"]:
            research_depth = result.metadata["research_config"]["depth"]
            result.metadata["research_depth"] = research_depth

        # 确保content_type_info在metadata["research_config"]中被保留
        # 首先检查result的metadata中是否已有此信息
        if "research_config" in result.metadata:
            # 首先检查workflow_result的metadata中的research_config是否有content_type_info
            if "research_config" in workflow_result.metadata and "content_type_info" in workflow_result.metadata["research_config"]:
                result.metadata["research_config"]["content_type_info"] = workflow_result.metadata["research_config"]["content_type_info"]
            # 然后检查当前研究配置中是否有content_type_info
            elif "content_type_info" in self.current_research_config:
                result.metadata["research_config"]["content_type_info"] = self.current_research_config["content_type_info"]

        logger.info("研究结果处理完成")
        return result

    def _extract_experts_from_insights(self, expert_insights_text: str) -> List:
        """从专家见解文本中提取专家信息

        Args:
            expert_insights_text: 专家见解文本

        Returns:
            List: 专家信息列表
        """
        # 简单实现，实际应用中可能需要更复杂的文本处理
        experts = []
        # 在真实应用中，这里应该使用NLP或模式匹配从文本中提取专家信息
        # 对于测试目的，我们只返回一个空列表
        return experts

    def _extract_article_outline(self, report_text: str, topic_title: str) -> Optional[List]:
        """从研究报告中提取文章大纲

        Args:
            report_text: 研究报告文本
            topic_title: 话题标题

        Returns:
            Optional[List]: 文章大纲项列表
        """
        # 简单实现，实际应用中可能需要更复杂的文本处理
        # 在真实应用中，这里应该使用NLP或模式匹配从文本中提取大纲结构
        return None

    def _workflow_result_to_basic_research(self, result: ResearchWorkflowResult) -> BasicResearch:
        """将ResearchWorkflowResult转换为BasicResearch

        Args:
            result: 研究工作流结果

        Returns:
            BasicResearch: 基础研究结果
        """
        # 创建BasicResearch对象
        research = BasicResearch(
            title=result.topic,
            content_type=result.metadata.get("research_config", {}).get("content_type", "article"),
            background=str(result.background_research) if result.background_research else None,
            data_analysis=str(result.data_analysis) if result.data_analysis else None,
            summary=str(result.research_report) if result.research_report else None,
            report=result.research_results,
            metadata=result.metadata
        )

        # 确保key_findings字段被初始化为空列表
        if not hasattr(research, 'key_findings') or research.key_findings is None:
            research.key_findings = []

        # 确保expert_insights字段被初始化为空列表
        if not hasattr(research, 'expert_insights') or research.expert_insights is None:
            research.expert_insights = []

        # 如果有专家信息，添加到研究结果中
        if result.experts:
            for expert in result.experts:
                if isinstance(expert, dict):
                    expert_insight = ExpertInsight(
                        expert_name=expert.get("name", "未知专家"),
                        content=expert.get("insight", "无见解内容"),
                        field=expert.get("field", None)
                    )
                    research.expert_insights.append(expert_insight)

        # 从研究报告中提取关键发现可以在未来添加
        # 目前我们只确保字段被正确初始化

        return research
