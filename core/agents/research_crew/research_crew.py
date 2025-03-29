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
from core.agents.research_crew.research_protocol import ResearchRequest, ResearchResponse, FactVerificationRequest, FactVerificationResponse
# 导入研究工具
from core.agents.research_crew.research_util import (
    extract_experts_from_insights, extract_key_findings, extract_sources,
    extract_verification_results, format_expert, create_research_config_from_request,
    workflow_result_to_basic_research
)
from core.agents.research_crew.research_result import ResearchWorkflowResult
from core.models.content_manager import ContentManager

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
        self.tasks = self.task_manager.get_all_tasks()
        logger.info(f"研究团队初始化完成，包含 {len(self.tasks)} 个任务")

        # 记录最近执行的工作流结果
        self.last_workflow_result = None

        # 当前研究配置
        self.current_research_config = {}

    async def research_topic(
        self,
        request: ResearchRequest
    ) -> ResearchResponse:
        """执行话题研究流程

        处理所有研究业务逻辑，根据传入的研究请求进行配置解析和智能体协调。
        这是研究团队的主要工作流程：
        1. 解析研究配置 - 从content_type_obj或research_instruct获取
        2. 背景研究：收集话题的基础信息和背景知识
        3. 专家发现：基于配置决定是否寻找专家观点
        4. 数据分析：基于配置决定是否执行数据分析
        5. 研究报告生成：整合所有结果生成研究报告

        Args:
            request: 研究请求对象，包含话题标题、内容类型对象和研究指导等信息

        Returns:
            ResearchResponse: 研究响应对象，包含所有研究结果
        """
        # 1. 从请求中提取基本信息
        topic_title = request.topic_title
        logger.info(f"开始研究话题: {topic_title}")

        # 2. 解析研究配置 - 按优先级处理
        # 2.1 获取内容类型对象
        content_type_obj = self._get_content_type_from_request(request)

        # 2.2 确定研究配置
        research_config = self._determine_research_config(request, content_type_obj)

        # 2.3 记录当前研究配置
        self.current_research_config = research_config
        logger.info(f"研究配置: {self.current_research_config}")

        # 3. 创建工作流结果跟踪对象
        workflow_result = ResearchWorkflowResult(topic=topic_title)
        self.last_workflow_result = workflow_result

        # 4. 根据研究配置决定执行哪些研究步骤
        research_depth = research_config.get("depth", "medium")
        needs_expert = research_config.get("needs_expert", True)
        needs_data_analysis = research_config.get("needs_data_analysis", False)

        logger.info(f"研究深度: {research_depth}, 需要专家: {needs_expert}, 需要数据分析: {needs_data_analysis}")

        try:
            # 4.1 背景研究 (始终执行)
            background_result = await self._execute_background_research(topic_title)
            workflow_result.background_research = background_result[0]

            # 4.2 专家观点研究 (根据配置决定)
            expert_result = None
            if needs_expert:
                expert_result = await self._execute_expert_research(topic_title, background_result[0])
                workflow_result.expert_insights = expert_result[0]
            else:
                logger.info(f"根据研究配置，跳过专家观点研究")

            # 4.3 数据分析 (根据配置决定)
            data_analysis_result = None
            if needs_data_analysis:
                data_analysis_result = await self._execute_data_analysis(topic_title, background_result[0])
                workflow_result.data_analysis = data_analysis_result[0]
            else:
                logger.info(f"根据研究配置，跳过数据分析")

            # 4.4 生成最终研究报告 (始终执行)
            report_result = await self._generate_research_report(
                topic_title,
                background_result[0],
                expert_result[0] if expert_result else None,
                data_analysis_result[0] if data_analysis_result else None
            )
            workflow_result.research_report = report_result[0]

            # 5. 提取和处理研究结果
            experts = extract_experts_from_insights(
                str(workflow_result.expert_insights) if workflow_result.expert_insights else ""
            )
            workflow_result.experts = experts
            workflow_result.research_results = str(workflow_result.research_report)

            # 6. 处理元数据
            # 6.1 添加研究配置到元数据
            workflow_result.metadata["research_config"] = self.current_research_config

            # 6.2 合并请求中的元数据
            if request.metadata:
                for key, value in request.metadata.items():
                    workflow_result.metadata[key] = value

            # 6.3 添加选项到元数据
            if request.options:
                for key, value in request.options.items():
                    workflow_result.metadata[key] = value

            # 7. 创建响应对象
            content_type_name = "article"  # 默认内容类型名称
            if content_type_obj:
                content_type_name = getattr(content_type_obj, 'name', "article")

            response = ResearchResponse(
                title=topic_title,
                content_type=content_type_name,
                background=str(workflow_result.background_research) if workflow_result.background_research else None,
                expert_insights=str(workflow_result.expert_insights) if workflow_result.expert_insights else None,
                data_analysis=str(workflow_result.data_analysis) if workflow_result.data_analysis else None,
                report=workflow_result.research_results,
                metadata=workflow_result.metadata,
                experts=[format_expert(e) for e in experts],
                key_findings=extract_key_findings(workflow_result.research_results),
                sources=extract_sources(workflow_result.research_results)
            )

            logger.info(f"话题'{topic_title}'研究完成")
            return response

        except Exception as e:
            logger.error(f"研究过程中出错: {e}")
            # 继续抛出异常以便上层处理
            raise e

    def _get_content_type_from_request(self, request: ResearchRequest) -> Optional[Any]:
        """从请求中获取内容类型对象

        按照以下优先级获取:
        1. 请求中直接提供的content_type_obj
        2. 如果没有content_type_obj，尝试从metadata中获取

        Args:
            request: 研究请求对象

        Returns:
            Optional[Any]: 内容类型对象，如果无法获取则返回None
        """
        # 1. 首先检查请求中是否直接提供了content_type_obj
        if request.content_type_obj:
            logger.info(f"使用请求中直接提供的内容类型对象")
            return request.content_type_obj

        # 2. 尝试从metadata中获取content_type_obj
        if request.metadata and "content_type_obj" in request.metadata:
            logger.info(f"从metadata中获取内容类型对象")
            return request.metadata["content_type_obj"]

        # 3. 无法获取内容类型对象
        logger.warning("请求中未提供内容类型对象")
        return None

    def _determine_research_config(self, request: ResearchRequest, content_type_obj: Optional[Any]) -> Dict[str, Any]:
        """确定研究配置

        按照以下优先级处理:
        1. 如果有content_type_obj，从中提取配置参数
        2. 如果有research_instruct，根据指导文本调整配置
        3. 否则使用默认配置

        Args:
            request: 研究请求对象
            content_type_obj: 内容类型对象

        Returns:
            Dict[str, Any]: 研究配置字典
        """
        # 初始化默认配置
        config = {
            "depth": "medium",
            "needs_expert": True,
            "needs_data_analysis": False,
            "max_sources": 10
        }

        # 1. 如果有内容类型对象，从中提取配置
        if content_type_obj:
            logger.info(f"从内容类型对象提取研究配置")

            # 获取内容类型名称
            if hasattr(content_type_obj, 'name'):
                config["content_type"] = content_type_obj.name

            # 获取研究深度
            if hasattr(content_type_obj, 'depth'):
                config["depth"] = content_type_obj.depth
                logger.info(f"研究深度: {config['depth']}")

            # 获取是否需要专家见解
            if hasattr(content_type_obj, 'needs_expert'):
                config["needs_expert"] = content_type_obj.needs_expert
                logger.info(f"需要专家: {config['needs_expert']}")

            # 获取是否需要数据分析
            if hasattr(content_type_obj, 'needs_data_analysis'):
                config["needs_data_analysis"] = content_type_obj.needs_data_analysis
                logger.info(f"需要数据分析: {config['needs_data_analysis']}")

            # 获取最大信息来源数量
            if hasattr(content_type_obj, 'max_sources'):
                config["max_sources"] = content_type_obj.max_sources

            # 获取内容类型摘要并添加到配置中
            if hasattr(content_type_obj, 'get_type_summary'):
                type_summary = content_type_obj.get_type_summary()
                if type_summary:
                    config["content_type_info"] = type_summary

        # 2. 如果有研究指导，根据指导调整配置
        if request.research_instruct:
            logger.info(f"根据研究指导调整配置")
            # 这里可以解析research_instruct文本，提取配置参数
            # 示例：如果指导中提到"深入研究"，则调整深度为"deep"
            if "深入研究" in request.research_instruct or "深度研究" in request.research_instruct:
                config["depth"] = "deep"
                logger.info(f"根据研究指导，调整研究深度为: {config['depth']}")

            # 添加研究指导到配置中
            config["research_instruct"] = request.research_instruct

        # 3. 合并请求选项到配置
        if request.options:
            for key, value in request.options.items():
                config[key] = value

        return config

    async def _execute_background_research(self, topic_title: str) -> Any:
        """执行背景研究任务

        Args:
            topic_title: 话题标题

        Returns:
            Any: 背景研究结果
        """
        logger.info("执行背景研究任务...")
        background_task = self.tasks["background_research"](topic_title)
        background_crew = Crew(
            agents=[self.agents["background_researcher"]],
            tasks=[background_task],
            verbose=True
        )
        return background_crew.kickoff()

    async def _execute_expert_research(self, topic_title: str, background_research: Any) -> Any:
        """执行专家观点研究任务

        Args:
            topic_title: 话题标题
            background_research: 背景研究结果

        Returns:
            Any: 专家观点研究结果
        """
        logger.info("执行专家观点研究任务...")
        expert_task = self.tasks["expert_finder"](topic_title, background_research)
        expert_crew = Crew(
            agents=[self.agents["expert_finder"]],
            tasks=[expert_task],
            verbose=True
        )
        return expert_crew.kickoff()

    async def _execute_data_analysis(self, topic_title: str, background_research: Any) -> Any:
        """执行数据分析任务

        Args:
            topic_title: 话题标题
            background_research: 背景研究结果

        Returns:
            Any: 数据分析结果
        """
        logger.info("执行数据分析任务...")
        data_task = self.tasks["data_analysis"](topic_title, background_research)
        data_crew = Crew(
            agents=[self.agents["data_analyst"]],
            tasks=[data_task],
            verbose=True
        )
        return data_crew.kickoff()

    async def _generate_research_report(
        self,
        topic_title: str,
        background_research: Any,
        expert_insights: Optional[Any] = None,
        data_analysis: Optional[Any] = None
    ) -> Any:
        """生成最终研究报告

        Args:
            topic_title: 话题标题
            background_research: 背景研究结果
            expert_insights: 专家观点结果，可选
            data_analysis: 数据分析结果，可选

        Returns:
            Any: 研究报告结果
        """
        logger.info("生成最终研究报告...")
        report_task = self.tasks["research_report"](
            topic_title,
            background_research,
            expert_insights,
            data_analysis
        )
        report_crew = Crew(
            agents=[self.agents["research_writer"]],
            tasks=[report_task],
            verbose=True
        )
        return report_crew.kickoff()

    async def verify_facts(
        self,
        request: FactVerificationRequest
    ) -> FactVerificationResponse:
        """执行事实验证流程

        验证一系列陈述的准确性和可靠性。
        此方法接收FactVerificationRequest对象，并返回FactVerificationResponse对象。

        Args:
            request: 事实验证请求对象，包含待验证陈述、验证彻底程度等

        Returns:
            FactVerificationResponse: 验证结果，包含每个陈述的验证结果
        """
        try:
            statements = request.statements
            thoroughness = request.thoroughness
            options = request.options

            logger.info(f"开始验证 {len(statements)} 个事实陈述，彻底程度: {thoroughness}")

            # 创建事实验证任务
            verification_task = self.tasks.get("fact_verification", None)
            if not verification_task:
                logger.error("事实验证任务未找到")
                raise ValueError("事实验证任务未定义")

            # 准备验证任务参数
            verification_task_instance = verification_task(
                statements=statements,
                thoroughness=thoroughness,
                options=options
            )

            # 使用事实验证智能体执行任务
            verification_crew = Crew(
                agents=[self.agents.get("fact_checker", self.agents["background_researcher"])],
                tasks=[verification_task_instance],
                verbose=True
            )

            # 执行验证
            verification_result = verification_crew.kickoff()
            result_text = verification_result[0] if verification_result else ""

            # 解析验证结果文本为结构化数据
            verification_results = extract_verification_results(result_text)

            # 准备元数据
            metadata = {
                "verification_time": datetime.now().isoformat(),
                "thoroughness": thoroughness
            }

            # 如果有其他选项，添加到元数据
            if options:
                metadata.update(options)

            # 创建响应对象
            response = FactVerificationResponse(
                results=verification_results,
                metadata=metadata
            )

            logger.info(f"事实验证完成，共验证 {len(verification_results)} 个陈述")
            return response

        except Exception as e:
            logger.error(f"执行事实验证过程中出错: {e}")
            # 创建一个包含错误信息的响应
            error_response = FactVerificationResponse(
                results=[],
                metadata={"error": str(e), "error_time": datetime.now().isoformat()}
            )
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
                result.experts = extract_experts_from_insights(expert_insights_text)
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
