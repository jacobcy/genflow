"""研究团队适配器模块

为研究团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, Union, List
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.topic import Topic
from core.models.research import BasicResearch, TopicResearch
from core.agents.research_crew import ResearchCrew
from core.agents.research_crew.research_protocol import ResearchRequest, ResearchResponse, FactVerificationRequest, FactVerificationResponse

class ResearchTeamAdapter(BaseTeamAdapter):
    """研究团队适配器 - 适配层

    这个类是研究系统的适配层，负责转换外部接口的数据格式，并调用实现层的功能。

    职责：
    1. 解析输入的话题信息（从Topic对象或topic_id）
    2. 根据content_type确定研究配置
    3. 创建ResearchRequest对象并调用ResearchCrew执行研究
    4. 将ResearchResponse转换为BasicResearch或TopicResearch对象
    5. 管理研究状态跟踪

    与三层架构的关系：
    - 属于适配层，负责接口转换和参数处理
    - 通过协议层的数据对象与实现层通信
    - 将实现层返回的结果转换为领域模型对象

    注意：本层不保存研究结果，只负责参数转换和调用下层
    """

    def __init__(self):
        super().__init__()
        self.crew = ResearchCrew()
        self._research_status = {}

    async def initialize(self, **kwargs) -> None:
        """初始化研究团队适配器

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("研究团队适配器初始化完成")

    async def research_topic(
        self,
        topic: Union[str, Topic, Dict, Any],
        depth: str = "medium",
        options: Optional[Dict[str, Any]] = None
    ) -> BasicResearch:
        """研究话题

        适配外部接口调用，转换为内部研究请求，并将结果转换为外部所需格式。

        Args:
            topic: 话题对象、字符串或包含话题信息的字典
            depth: 研究深度(shallow/medium/deep)
            options: 其他选项

        Returns:
            BasicResearch: 研究结果，如有topic_id则返回TopicResearch
        """
        try:
            # 1. 提取基本话题信息
            topic_title, topic_id, content_type = self._extract_topic_info(topic)

            # 记录研究状态
            if topic_id:
                self._research_status[topic_id] = "in_progress"

            # 使用默认内容类型（如果未指定）
            if not content_type:
                content_type = "article"

            # 2. 准备元数据
            metadata = {}

            # 如果有内容类型对象，添加到元数据
            try:
                content_type_obj = ContentManager.get_content_type(content_type)
                if content_type_obj:
                    metadata["content_type_info"] = content_type_obj.get_type_summary()
            except Exception:
                pass

            # 3. 准备选项
            research_options = options or {}

            # 添加平台信息（如果有）
            if hasattr(topic, 'platform') and topic.platform:
                research_options["platform_id"] = topic.platform.id if hasattr(topic.platform, 'id') else str(topic.platform)

            # 4. 创建研究请求对象
            request = ResearchRequest(
                topic_title=topic_title,
                content_type=content_type,
                depth=depth,
                options=research_options,
                metadata=metadata,
                topic_id=topic_id
            )

            # 5. 调用研究团队执行研究
            logger.info(f"开始调用研究团队执行话题研究: {topic_title}")
            response = await self.crew.research_topic(request)

            # 6. 转换结果
            if topic_id:
                self._research_status[topic_id] = "completed"
                # 如果有topic_id，转换为TopicResearch
                return self._to_topic_research(response, topic_id)

            # 没有topic_id，转换为BasicResearch
            return self._to_basic_research(response)

        except Exception as e:
            if topic_id:
                self._research_status[topic_id] = "failed"
            raise RuntimeError(f"研究话题失败: {str(e)}")

    def _to_basic_research(self, response: ResearchResponse) -> BasicResearch:
        """将ResearchResponse转换为BasicResearch

        Args:
            response: 研究响应对象

        Returns:
            BasicResearch: 基础研究结果
        """
        from core.models.research import ExpertInsight, KeyFinding, Source

        # 转换专家见解
        expert_insights = []
        for expert in response.experts:
            insight = ExpertInsight(
                expert_name=expert.get("name", "未知专家"),
                content=expert.get("insight", ""),
                field=expert.get("field", None),
                credentials=expert.get("credentials", None)
            )
            expert_insights.append(insight)

        # 转换关键发现
        key_findings = []
        for finding in response.key_findings:
            kf = KeyFinding(
                content=finding.get("content", ""),
                importance=finding.get("importance", 0.5),
                sources=[]
            )
            key_findings.append(kf)

        # 转换信息来源
        sources = []
        for source in response.sources:
            src = Source(
                name=source.get("name", "未知来源"),
                url=source.get("url", None),
                author=source.get("author", None),
                publish_date=source.get("date", None),
                content_snippet=source.get("snippet", None),
                reliability_score=source.get("reliability", 0.5)
            )
            sources.append(src)

        # 创建BasicResearch对象
        return BasicResearch(
            title=response.title,
            content_type=response.content_type,
            background=response.background,
            expert_insights=expert_insights,
            key_findings=key_findings,
            sources=sources,
            data_analysis=response.data_analysis,
            report=response.report,
            metadata=response.metadata
        )

    def _to_topic_research(self, response: ResearchResponse, topic_id: str) -> TopicResearch:
        """将ResearchResponse转换为TopicResearch

        Args:
            response: 研究响应对象
            topic_id: 话题ID

        Returns:
            TopicResearch: 话题研究结果
        """
        basic_research = self._to_basic_research(response)
        return TopicResearch.from_basic_research(basic_research, topic_id)

    def _extract_topic_info(self, topic) -> tuple:
        """从输入的topic提取关键信息

        Args:
            topic: 话题对象、字符串或字典

        Returns:
            tuple: (topic_title, topic_id, content_type)
        """
        topic_title = ""
        topic_id = None
        content_type = None

        if isinstance(topic, str):
            topic_title = topic
        else:
            # 从Topic对象或字典中提取信息
            topic_id = getattr(topic, 'id', None) if not isinstance(topic, dict) else topic.get('id')
            topic_title = getattr(topic, 'title', str(topic)) if not isinstance(topic, dict) else topic.get('title', str(topic))

            # 尝试获取content_type
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type = topic.content_type
            elif isinstance(topic, dict) and 'content_type' in topic:
                content_type = topic['content_type']
            elif hasattr(topic, 'categories') and topic.categories:
                # 尝试从第一个分类推断内容类型
                primary_category = topic.categories[0] if topic.categories else None
                if primary_category:
                    content_type_obj = ContentManager.get_content_type_by_category(primary_category)
                    if content_type_obj:
                        content_type = content_type_obj.id

        return topic_title, topic_id, content_type

    def _determine_depth_from_content_type(self, content_type_obj) -> str:
        """根据内容类型确定研究深度

        Args:
            content_type_obj: 内容类型对象

        Returns:
            str: 研究深度(shallow/medium/deep)
        """
        research_level = getattr(content_type_obj, 'research_level', 3)
        if research_level <= 1:
            return "shallow"
        elif research_level >= 4:
            return "deep"
        else:
            return "medium"

    def _get_platform_info(self, topic) -> dict:
        """获取平台信息

        Args:
            topic: 话题对象

        Returns:
            dict: 平台信息
        """
        platform_info = {}
        if hasattr(topic, 'platform') and topic.platform:
            platform = ContentManager.get_platform(topic.platform)
            if platform:
                platform_info = {
                    "platform_id": platform.id,
                    "platform_info": platform.to_dict()
                }
        return platform_info

    def _prepare_research_options(self, options, content_type_obj, platform_info) -> dict:
        """准备研究选项

        Args:
            options: 用户提供的选项
            content_type_obj: 内容类型对象
            platform_info: 平台信息

        Returns:
            dict: 完整的研究选项
        """
        merged_options = options or {}

        # 添加内容类型信息
        if content_type_obj:
            merged_options["content_type"] = content_type_obj.id
            merged_options["content_type_info"] = content_type_obj.get_type_summary()

        # 添加平台信息
        if platform_info:
            merged_options.update(platform_info)

        return merged_options

    def _create_research_config(self, content_type: str, content_type_obj=None) -> Dict[str, Any]:
        """根据内容类型创建研究配置

        Args:
            content_type: 内容类型ID
            content_type_obj: 内容类型对象(可选)

        Returns:
            Dict[str, Any]: 研究配置字典
        """
        # 从ResearchCrew获取基础配置
        from core.agents.research_crew.research_crew import get_research_config
        research_config = get_research_config(content_type)

        # 添加内容类型信息
        if content_type_obj:
            research_config["content_type_info"] = content_type_obj.get_type_summary()
        else:
            # 尝试从ContentManager获取内容类型对象
            try:
                ct_obj = ContentManager.get_content_type(content_type)
                if ct_obj:
                    research_config["content_type_info"] = ct_obj.get_type_summary()
            except Exception:
                # 如果获取失败，使用内容类型ID作为信息
                research_config["content_type_info"] = content_type

        return research_config

    async def verify_facts(
        self,
        statements: List[str],
        thoroughness: str = "high",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """验证事实陈述的准确性

        Args:
            statements: 需要验证的陈述列表
            thoroughness: 验证彻底程度(low/medium/high)
            options: 其他选项

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 创建事实验证请求对象
            request = FactVerificationRequest(
                statements=statements,
                thoroughness=thoroughness,
                options=options or {}
            )

            # 调用ResearchCrew执行事实验证
            logger.info(f"开始验证 {len(statements)} 个事实陈述")
            response = await self.crew.verify_facts(request)

            # 直接返回验证结果
            return {
                "results": response.results,
                "metadata": response.metadata
            }
        except Exception as e:
            raise RuntimeError(f"验证事实失败: {str(e)}")

    async def get_research_status(self, topic_id: str) -> str:
        """获取指定话题ID的研究状态

        Args:
            topic_id: 话题ID

        Returns:
            str: 研究状态(pending/in_progress/completed/failed)
        """
        return self._research_status.get(topic_id, "pending")
