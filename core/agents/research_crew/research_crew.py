"""研究团队管理模块

这个模块定义了研究团队的组织和工作流程，负责协调各个研究智能体的工作，
完成从话题研究到生成研究报告的全流程。
"""
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from datetime import datetime

from crewai import Crew, Task, Agent
from core.config import Config
from core.agents.research_crew.research_agents import ResearchAgents
from core.agents.research_crew.research_tasks import ResearchTasks
from core.agents.research_crew.research_protocol import ResearchRequest, ResearchResponse
# 导入研究工具
from core.agents.research_crew.research_util import (
    RESEARCH_DEPTH_LIGHT, RESEARCH_DEPTH_MEDIUM, RESEARCH_DEPTH_DEEP,
    DEFAULT_RESEARCH_CONFIG, RESEARCH_CONFIG,
    get_research_config,
    extract_experts_from_insights, extract_key_findings, extract_sources,
    format_expert, create_research_config_from_request, map_research_depth
)
from core.agents.research_crew.research_result import ResearchWorkflowResult

# 配置日志
logger = logging.getLogger("research_crew")

class ResearchCrew:
    """研究团队类 - 实现层

    这个类是研究系统的实现层，负责执行具体的研究任务，协调各个研究智能体的工作。
    它不直接处理topic_id关联或领域模型映射，而是专注于研究过程本身。

    职责：
    1. 接收ResearchRequest对象并执行研究流程
    2. 返回ResearchResponse对象给适配层
    3. 管理研究智能体和工作流程
    4. 不直接与控制器交互，只与适配层通信

    与三层架构的关系：
    - 属于实现层，专注于核心业务逻辑
    - 通过协议层的数据对象与适配层通信
    - 不关心数据持久化或外部系统集成
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

        # 创建任务管理器
        self.task_manager = ResearchTasks(config=self.config)

        # 创建任务列表
        self.tasks = self.task_manager.create_all_tasks()
        logger.info(f"研究团队初始化完成，包含 {len(self.tasks)} 个任务")

        # 记录最近执行的工作流结果
        self.last_workflow_result = None

        # 使用统一的配置
        self.content_type_config = RESEARCH_CONFIG

        # 默认内容类型配置
        self.default_research_config = DEFAULT_RESEARCH_CONFIG.copy()

        # 当前研究配置
        self.current_research_config = self.default_research_config.copy()


    async def research_topic(
        self,
        request: ResearchRequest
    ) -> ResearchResponse:
        """执行话题研究流程

        处理所有研究业务逻辑，包括研究配置生成、智能体协调和结果处理。
        这是研究团队的主要工作流程，按以下步骤执行：
        1. 处理研究配置和参数
        2. 背景研究：收集话题的基础信息和背景知识
        3. 专家发现：寻找并分析相关领域专家的观点和见解
        4. 数据分析：分析与话题相关的数据和趋势
        5. 研究报告生成：整合前三步的结果，生成完整的研究报告

        Args:
            request: 研究请求对象，包含话题标题、内容类型等信息

        Returns:
            ResearchResponse: 研究响应对象，包含所有研究结果
        """
        # 从请求中提取参数
        topic_title = request.topic_title
        content_type = request.content_type
        depth = request.depth
        options = request.options
        metadata = request.metadata

        logger.info(f"开始研究话题: {topic_title}")

        # 1. 生成研究配置
        research_config = self._create_research_config_from_request(request)

        # 2. 设置研究配置
        self.current_research_config = research_config.copy()

        logger.info(f"研究配置: {self.current_research_config}")

        # 创建工作流结果跟踪对象
        workflow_result = ResearchWorkflowResult(topic=topic_title)
        self.last_workflow_result = workflow_result

        # 根据研究配置决定是否需要专家和数据分析
        needs_expert = self.current_research_config.get("needs_expert", True)
        needs_data_analysis = self.current_research_config.get("needs_data_analysis", True)

        try:
            # 第1步：背景研究 (始终执行)
            background_task = self.tacks["background_research"](topic_title)

            # 使用单智能体执行任务
            logger.info("执行背景研究任务...")
            background_crew = Crew(
                agents=[self.agents["background_researcher"]],
                tasks=[background_task],
                verbose=True
            )
            background_result = background_crew.kickoff()
            workflow_result.background_research = background_result[0]

            # 第2步：专家观点研究（可选）
            expert_result = None
            if needs_expert:
                expert_task = self.tasks["expert_finder"](
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
            else:
                logger.info(f"根据研究配置，跳过专家观点研究")

            # 第3步：数据分析（可选）
            data_analysis_result = None
            if needs_data_analysis:
                data_task = self.tasks["data_analysis"](
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
            else:
                logger.info(f"根据研究配置，跳过数据分析")

            # 第4步：生成最终研究报告（始终执行）
            report_task = self.tasks["research_report"](
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

            # 提取专家列表
            experts = self._extract_experts_from_insights(
                str(workflow_result.expert_insights) if workflow_result.expert_insights else ""
            )
            workflow_result.experts = experts

            # 处理研究报告
            workflow_result.research_results = str(workflow_result.research_report)

            # 保存研究配置到元数据
            workflow_result.metadata["research_config"] = self.current_research_config

            # 合并请求中的元数据
            if metadata:
                for key, value in metadata.items():
                    workflow_result.metadata[key] = value

            # 添加选项到元数据
            if options:
                for key, value in options.items():
                    workflow_result.metadata[key] = value

            # 创建响应对象
            response = ResearchResponse(
                title=topic_title,
                content_type=content_type,
                background=str(workflow_result.background_research) if workflow_result.background_research else None,
                expert_insights=str(workflow_result.expert_insights) if workflow_result.expert_insights else None,
                data_analysis=str(workflow_result.data_analysis) if workflow_result.data_analysis else None,
                report=workflow_result.research_results,
                metadata=workflow_result.metadata,
                experts=[self._format_expert(e) for e in experts],
                key_findings=self._extract_key_findings(workflow_result.research_results),
                sources=self._extract_sources(workflow_result.research_results)
            )

            logger.info(f"话题'{topic_title}'研究完成")
            return response

        except Exception as e:
            logger.error(f"研究过程中出错: {e}")
            # 继续抛出异常以便上层处理
            raise e


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
