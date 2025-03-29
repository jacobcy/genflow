"""研究团队适配器模块

为研究团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, Union, List
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.topic.topic import Topic
from core.models.research.research import BasicResearch, TopicResearch
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
        topic_id: str,
        topic_title: str,
        topic: Union[Topic, Dict[str, Any], Any],
        content_type_obj: Optional[Any] = None,
        research_instruct: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> BasicResearch:
        """研究话题

        适配外部接口调用，转换为内部研究请求，并将结果转换为外部所需格式。

        Args:
            topic_id: 话题ID
            topic_title: 话题标题
            topic: 话题对象、字符串或包含话题信息的字典
            content_type_obj: 内容类型对象，直接传递给研究团队，优先级高
            research_instruct: 研究指导文本，描述如何研究该话题
            options: 其他研究选项

        Returns:
            BasicResearch: 研究结果，如有topic_id则返回TopicResearch
        """
        try:
            # 1. 提取基本话题信息
            topic_title, topic_id, content_type_name = self._extract_topic_info(topic)

            # 记录研究状态
            if topic_id:
                self._research_status[topic_id] = "in_progress"

            # 2. 确定内容类型对象
            if content_type_obj is None:
                # 如果没有直接传递content_type_obj，尝试获取
                try:
                    # 首先尝试通过content_type_name获取
                    if content_type_name:
                        content_type_obj = ContentManager.get_content_type(content_type_name)
                        if content_type_obj:
                            logger.info(f"通过content_type_name获取内容类型对象: {content_type_obj.name}")

                    # 如果还是没有，使用默认内容类型
                    if content_type_obj is None:
                        content_type_obj = ContentManager.get_default_content_type()
                        logger.info(f"使用默认内容类型对象: {content_type_obj.name}")
                except Exception as e:
                    logger.error(f"获取内容类型对象失败: {e}")
                    # 这里不再设置默认值，让协议层处理默认内容类型

            # 3. 准备元数据
            metadata = {}

            # 如果有内容类型对象，添加到元数据
            if content_type_obj:
                metadata["content_type_obj"] = content_type_obj.dict() if hasattr(content_type_obj, 'dict') else vars(content_type_obj)

            # 如果有研究指导，添加到元数据
            if research_instruct:
                metadata["research_instruct"] = research_instruct

            # 4. 准备平台信息
            try:
                if topic and hasattr(topic, 'platform') and getattr(topic, 'platform', None):
                    platform_info = self._get_platform_info(topic)
                    if platform_info and options:
                        options.update(platform_info)
                    elif platform_info:
                        options = platform_info
            except Exception as e:
                logger.warning(f"处理平台信息失败: {e}")

            # 5. 创建研究请求对象
            request = ResearchRequest(
                topic_title=topic_title,
                content_type_obj=content_type_obj,  # 直接传递内容类型对象
                research_instruct=research_instruct,  # 直接传递研究指导
                options=options or {},
                metadata=metadata,
                topic_id=topic_id
            )

            # 6. 调用研究团队执行研究
            logger.info(f"开始调用研究团队执行话题研究: {topic_title}")
            response = await self.crew.research_topic(request)

            # 7. 转换结果
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
        from core.models.research.research import ExpertInsight, KeyFinding, Source

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
        elif isinstance(topic, dict):
            # 从字典中提取信息
            topic_id = topic.get('id')
            topic_title = topic.get('title', str(topic))

            # 从字典中获取content_type
            if 'content_type' in topic:
                content_type = topic['content_type']
        else:
            # 从Topic对象中提取信息
            topic_id = getattr(topic, 'id', None)
            topic_title = getattr(topic, 'title', str(topic))

            # 从对象获取content_type
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type = topic.content_type

            # 尝试从分类推断内容类型
            if hasattr(topic, 'categories') and topic.categories and not content_type:
                # 尝试从第一个分类推断内容类型
                primary_category = topic.categories[0] if topic.categories else None
                if primary_category:
                    # 使用ContentManager从category获取content_type
                    content_type_obj = ContentManager.get_content_type_by_category(primary_category)
                    if content_type_obj:
                        # 获取content_type ID
                        content_type = content_type_obj.id

        return topic_title, topic_id, content_type

    def _get_platform_info(self, topic) -> dict:
        """获取平台信息

        Args:
            topic: 话题对象

        Returns:
            dict: 平台信息
        """
        platform_info = {}
        if hasattr(topic, 'platform') and getattr(topic, 'platform', None):
            platform = ContentManager.get_platform(topic.platform)
            if platform:
                platform_info = {
                    "platform_id": platform.id,
                    "platform_info": platform.to_dict()
                }
        return platform_info

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
