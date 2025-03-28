"""研究任务模块

包含研究团队使用的任务创建和执行逻辑，将任务设置与核心业务逻辑分离。
该模块通过 ResearchTasks 类提供标准化的任务创建接口，支持不同深度和类型的研究任务。
"""

import logging
from typing import Dict, Any, Optional, Mapping
from crewai import Task, Agent
from crewai.tasks.task_output import TaskOutput
from core.config import Config
from core.agents.research_crew.research_util import (
    RESEARCH_DEPTH_LIGHT,
    RESEARCH_DEPTH_MEDIUM,
    RESEARCH_DEPTH_DEEP,
    map_research_depth
)

# 配置日志
logger = logging.getLogger("research_tasks")


class ResearchTasks:
    """研究任务管理类

    负责创建和配置不同类型的研究任务，包括背景研究、专家发现、数据分析和研究报告等。
    根据研究配置自动调整任务的详细程度和要求。

    属性:
        config: 系统配置对象
        agents: 可用于执行任务的智能体字典
        current_research_config: 当前研究配置
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化研究任务类

        Args:
            config: 可选的配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self.agents = {}  # 将由外部设置
        self.current_research_config = {}  # 将由外部设置

    def set_agents(self, agents: Dict[str, Agent]) -> None:
        """设置可用的智能体

        Args:
            agents: 智能体名称到智能体对象的映射
        """
        self.agents = agents

    def set_research_config(self, research_config: Dict[str, Any]) -> None:
        """设置当前研究配置

        Args:
            research_config: 研究配置信息
        """
        self.current_research_config = research_config

    def create_background_research_task(self, topic: str) -> Task:
        """创建背景研究任务

        根据研究配置创建适合的背景研究任务，任务深度和要求会根据研究配置自动调整。

        Args:
            topic: 研究话题

        Returns:
            Task: 配置好的背景研究任务
        """
        logger.info(f"创建背景研究任务，话题: {topic}")

        # 获取和映射研究深度
        research_depth = self.current_research_config.get("depth", RESEARCH_DEPTH_MEDIUM)
        depth_level = map_research_depth(research_depth)

        # 根据研究深度调整任务描述
        depth_instructions = {
            "low": "进行快速但全面的背景调查，重点关注最基本的信息和关键事实。不需要深入历史发展和复杂概念解释。",
            "medium": "进行标准深度的背景研究，平衡全面性和深度，包括基本历史背景和主要概念解释。",
            "high": "进行深入全面的背景研究，详细探索历史发展、相关理论基础，并提供全面的概念解释和最新研究进展。"
        }

        # 获取内容类型信息
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

        # 确保必要的智能体可用
        if "background_researcher" not in self.agents:
            raise ValueError("未找到背景研究智能体")

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["background_researcher"]
        )

    def create_expert_finder_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建专家发现任务

        根据研究配置和背景研究结果创建专家发现任务，深度和专家数量会根据研究配置自动调整。

        Args:
            topic: 研究话题
            background_research: 背景研究结果

        Returns:
            Task: 配置好的专家发现任务
        """
        logger.info(f"创建专家发现任务，话题: {topic}")

        # 获取和映射研究深度
        research_depth = self.current_research_config.get("depth", RESEARCH_DEPTH_MEDIUM)
        depth_level = map_research_depth(research_depth)

        # 获取内容类型信息
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 根据深度调整专家数量
        expert_counts = {
            "low": "2-3位",
            "medium": "3-5位",
            "high": "5-7位"
        }

        # 构建任务描述
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

        # 确保必要的智能体可用
        if "expert_finder" not in self.agents:
            raise ValueError("未找到专家发现智能体")

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["expert_finder"]
        )

    def create_data_analysis_task(self, topic: str, background_research: TaskOutput) -> Task:
        """创建数据分析任务

        根据研究配置和背景研究结果创建数据分析任务，分析深度会根据研究配置自动调整。

        Args:
            topic: 研究话题
            background_research: 背景研究结果

        Returns:
            Task: 配置好的数据分析任务
        """
        logger.info(f"创建数据分析任务，话题: {topic}")

        # 获取和映射研究深度
        research_depth = self.current_research_config.get("depth", RESEARCH_DEPTH_MEDIUM)
        depth_level = map_research_depth(research_depth)

        # 获取内容类型信息
        content_type_info = self.current_research_config.get("content_type_info", "一般")
        content_type_display = content_type_info if isinstance(content_type_info, str) else "一般"

        # 根据研究深度调整任务描述
        data_requirements = {
            "low": "收集基本统计数据和关键趋势，不需要深入分析",
            "medium": "收集足够的数据点，包括趋势分析和简单预测",
            "high": "进行全面深入的数据收集和分析，包括详细的统计分析和多维度比较"
        }

        # 构建任务描述
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

        # 确保必要的智能体可用
        if "data_analyst" not in self.agents:
            raise ValueError("未找到数据分析智能体")

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["data_analyst"]
        )

    def create_research_report_task(
        self,
        topic: str,
        background_research: TaskOutput,
        expert_insights: Optional[TaskOutput] = None,
        data_analysis: Optional[TaskOutput] = None
    ) -> Task:
        """创建研究报告任务

        整合前序任务结果，创建最终研究报告任务，报告的深度和详尽程度会根据研究配置自动调整。

        Args:
            topic: 研究话题
            background_research: 背景研究结果
            expert_insights: 专家观点结果（可选）
            data_analysis: 数据分析结果（可选）

        Returns:
            Task: 配置好的研究报告任务
        """
        logger.info(f"创建研究报告任务，话题: {topic}")

        # 获取和映射研究深度
        research_depth = self.current_research_config.get("depth", RESEARCH_DEPTH_MEDIUM)
        depth_level = map_research_depth(research_depth)

        # 获取内容类型信息
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

        # 确保必要的智能体可用
        if "research_writer" not in self.agents:
            raise ValueError("未找到研究报告撰写智能体")

        return Task(
            description=description,
            expected_output=expected_outputs[depth_level],
            agent=self.agents["research_writer"]
        )

    def create_all_tasks(self, topic: str, background_research: Optional[TaskOutput] = None) -> Dict[str, Task]:
        """创建所有研究任务

        为完整研究流程创建所有必要的任务。注意：如果不提供background_research，则只能创建背景研究任务。

        Args:
            topic: 研究话题
            background_research: 背景研究结果，用于创建后续任务

        Returns:
            Dict[str, Task]: 任务名称到任务对象的映射
        """
        tasks = {
            "background_research": self.create_background_research_task(topic)
        }

        # 如果有背景研究结果，创建后续任务
        if background_research:
            tasks.update({
                "expert_finder": self.create_expert_finder_task(topic, background_research),
                "data_analysis": self.create_data_analysis_task(topic, background_research)
            })

            # 研究报告任务需要背景研究，但expert_insights和data_analysis是可选的
            tasks["research_report"] = self.create_research_report_task(
                topic,
                background_research
            )

        return tasks
