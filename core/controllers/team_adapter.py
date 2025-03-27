"""团队适配器模块

为各个专业团队提供统一的接口适配层，处理参数转换和错误处理。
使用 ContentManager 提供的内容类型和文章风格管理功能。
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from loguru import logger

from core.models.content_manager import ContentManager
from core.models.topic import Topic

from core.agents.topic_crew import TopicCrew
from core.agents.research_crew import ResearchCrew
from core.agents.writing_crew import WritingCrew
from core.agents.style_crew import StyleCrew
from core.agents.review_crew import ReviewCrew

class BaseTeamAdapter(ABC):
    """团队适配器基类"""

    def __init__(self):
        """初始化适配器"""
        self._progress = 0
        self._initialized = False

    async def initialize(self, **kwargs) -> None:
        """初始化团队

        Args:
            **kwargs: 初始化参数
        """
        # 确保 ContentManager 已经初始化
        ContentManager.ensure_initialized()
        self._initialized = True

    def get_progress(self) -> float:
        """获取当前进度

        Returns:
            float: 0-1之间的进度值
        """
        return self._progress

    @property
    def initialized(self) -> bool:
        """是否已初始化"""
        return self._initialized

class TopicTeamAdapter(BaseTeamAdapter):
    """选题团队适配器"""

    def __init__(self):
        super().__init__()
        self.crew = TopicCrew()

    async def initialize(self, **kwargs) -> None:
        """初始化选题团队

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("选题团队适配器初始化完成")

    async def generate_topics(
        self,
        category: Optional[str] = None,
        count: int = 5,
        options: Optional[Dict[str, Any]] = None
    ) -> List[Topic]:
        """生成话题建议

        Args:
            category: 话题分类
            count: 生成数量
            options: 其他选项

        Returns:
            List[Topic]: 话题列表
        """
        try:
            # 尝试通过ContentManager获取类别对应的内容类型
            content_type = None
            if category:
                content_type = ContentManager.get_content_type_by_category(category)
                if content_type:
                    logger.info(f"找到分类 '{category}' 对应的内容类型: {content_type.id}")
                else:
                    logger.warning(f"未找到分类 '{category}' 对应的内容类型，使用原始分类")

            # 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()

            # 默认使用非自动模式，除非在选项中指定
            auto_mode = merged_options.pop("auto_mode", False)

            result = await self.crew.run_workflow(
                category=category,
                count=count,
                auto_mode=auto_mode,
                **merged_options
            )
            return result
        except Exception as e:
            raise RuntimeError(f"生成话题失败: {str(e)}")

    async def evaluate_topic(
        self,
        topic: Topic,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """评估话题价值

        Args:
            topic: 话题对象
            options: 评估选项

        Returns:
            Dict[str, Any]: 评估结果
        """
        try:
            # 获取话题对应的内容类型
            content_type = None
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type = ContentManager.get_content_type(topic.content_type)
            elif hasattr(topic, 'category') and topic.category:
                # 尝试从分类推断内容类型
                content_type = ContentManager.get_content_type_by_category(topic.category)

            # 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
                logger.info(f"话题评估使用内容类型: {content_type.id}")

            result = await self.crew.evaluate_topic(
                topic,
                **merged_options
            )
            return result
        except Exception as e:
            raise RuntimeError(f"评估话题失败: {str(e)}")

class ResearchTeamAdapter(BaseTeamAdapter):
    """研究团队适配器"""

    def __init__(self):
        super().__init__()
        self.crew = ResearchCrew()
        self._research_status = {}

    async def initialize(self, **kwargs) -> None:
        """初始化研究团队

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("研究团队适配器初始化完成")

    async def research_topic(
        self,
        topic: Topic,
        depth: str = "medium",
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """研究话题

        Args:
            topic: 话题对象
            depth: 研究深度(shallow/medium/deep)
            options: 其他选项

        Returns:
            Dict[str, Any]: 研究结果
        """
        try:
            # 获取话题对应的内容类型
            content_type = None
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type = ContentManager.get_content_type(topic.content_type)
            elif hasattr(topic, 'categories') and topic.categories:
                # 尝试从第一个分类推断内容类型
                primary_category = topic.categories[0] if topic.categories else None
                if primary_category:
                    content_type = ContentManager.get_content_type_by_category(primary_category)

            # 根据内容类型调整研究深度
            if content_type and not depth:
                # 根据内容类型的research_intensity属性设置研究深度
                research_level = getattr(content_type.characteristics, 'research_intensity', 3)
                if research_level <= 1:
                    depth = "shallow"
                elif research_level >= 4:
                    depth = "deep"
                else:
                    depth = "medium"
                logger.info(f"根据内容类型 {content_type.id} 设置研究深度: {depth}")

            # 获取平台信息
            platform = None
            if hasattr(topic, 'platform') and topic.platform:
                platform = ContentManager.get_platform(topic.platform)

            # 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
            if platform:
                merged_options["platform"] = platform.id
                merged_options["platform_info"] = platform.to_dict()

            # 确保使用正确的方法名
            result = await self.crew.research_topic(
                topic=topic,
                depth=depth,
                **merged_options
            )
            self._research_status[topic.id] = "completed"
            return result
        except Exception as e:
            self._research_status[topic.id] = "failed"
            raise RuntimeError(f"研究话题失败: {str(e)}")

    async def get_research_status(self, topic_id: str) -> str:
        """获取研究状态

        Args:
            topic_id: 话题ID

        Returns:
            str: 研究状态
        """
        return self._research_status.get(topic_id, "not_found")

class WritingTeamAdapter(BaseTeamAdapter):
    """写作团队适配器"""

    def __init__(self):
        super().__init__()
        self.crew = WritingCrew()
        self._writing_status = {}

    async def initialize(self, **kwargs) -> None:
        """初始化写作团队

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("写作团队适配器初始化完成")

    async def write_content(
        self,
        topic: Topic,
        research_data: Dict[str, Any],
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """写作内容

        Args:
            topic: 话题对象
            research_data: 研究资料
            style: 写作风格
            options: 其他选项

        Returns:
            Dict[str, Any]: 写作结果
        """
        try:
            # 获取话题对应的内容类型
            content_type = None
            content_type_id = None
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type_id = topic.content_type
                content_type = ContentManager.get_content_type(content_type_id)
            elif hasattr(topic, 'categories') and topic.categories:
                # 尝试从第一个分类推断内容类型
                primary_category = topic.categories[0] if topic.categories else None
                if primary_category:
                    content_type = ContentManager.get_content_type_by_category(primary_category)
                    if content_type:
                        content_type_id = content_type.id

            # 获取平台信息
            platform = None
            platform_id = None
            if hasattr(topic, 'platform') and topic.platform:
                platform_id = topic.platform
                platform = ContentManager.get_platform(platform_id)

            # 处理文章风格
            article_style = None
            if style:
                # 如果指定了风格，直接使用
                article_style = ContentManager.get_article_style(style)
            elif platform_id:
                # 尝试根据平台获取文章风格
                article_style = ContentManager.get_platform_style(platform_id)

            # 如果有内容类型但没有风格，获取推荐风格
            if content_type_id and not article_style:
                article_style = ContentManager.get_recommended_style_for_content_type(content_type_id)
                if article_style:
                    logger.info(f"为内容类型 {content_type_id} 推荐风格: {article_style.id}")

            # 检查内容类型和风格是否兼容
            if content_type_id and article_style and article_style.id:
                is_compatible = ContentManager.is_compatible(content_type_id, article_style.id)
                if not is_compatible:
                    logger.warning(f"内容类型 {content_type_id} 与风格 {article_style.id} 不兼容，尝试寻找替代方案")
                    # 尝试获取兼容风格
                    article_style = ContentManager.get_recommended_style_for_content_type(content_type_id)
                    if article_style:
                        logger.info(f"使用兼容风格: {article_style.id}")

            # 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
            if article_style:
                merged_options["style"] = article_style.id
                merged_options["style_info"] = article_style.get_style_summary()
            if platform:
                merged_options["platform"] = platform.id
                merged_options["platform_info"] = platform.to_dict()

            # 确保风格参数正确
            style_param = article_style.id if article_style else style

            # 确保使用正确的方法名
            result = await self.crew.write_article(
                article=topic,
                research_data=research_data,
                platform=platform_id,
                content_type=content_type_id,
                style=style_param,
                **merged_options
            )
            self._writing_status[topic.id] = "completed"
            return result
        except Exception as e:
            self._writing_status[topic.id] = "failed"
            raise RuntimeError(f"写作内容失败: {str(e)}")

    async def get_writing_status(self, topic_id: str) -> str:
        """获取写作状态

        Args:
            topic_id: 话题ID

        Returns:
            str: 写作状态
        """
        return self._writing_status.get(topic_id, "not_found")

class StyleTeamAdapter(BaseTeamAdapter):
    """风格团队适配器"""

    def __init__(self):
        super().__init__()
        self.crew = StyleCrew()

    async def initialize(self, **kwargs) -> None:
        """初始化风格团队

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("风格团队适配器初始化完成")

    async def apply_style(
        self,
        topic: Topic,
        content: str,
        style: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """应用风格

        Args:
            topic: 话题对象
            content: 原始内容
            style: 目标风格
            options: 其他选项

        Returns:
            str: 调整后的内容
        """
        try:
            # 获取风格配置
            article_style = ContentManager.get_article_style(style)
            if not article_style:
                logger.warning(f"未找到风格: {style}，尝试平台匹配")
                if hasattr(topic, 'platform') and topic.platform:
                    article_style = ContentManager.get_platform_style(topic.platform)
                    if article_style:
                        logger.info(f"使用平台 {topic.platform} 对应的风格: {article_style.id}")

            # 获取内容类型
            content_type = None
            content_type_id = None
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type_id = topic.content_type
                content_type = ContentManager.get_content_type(content_type_id)

            # 获取平台信息
            platform = None
            platform_id = None
            if hasattr(topic, 'platform') and topic.platform:
                platform_id = topic.platform
                platform = ContentManager.get_platform(platform_id)

            # 检查兼容性
            if content_type_id and article_style and article_style.id:
                is_compatible = ContentManager.is_compatible(content_type_id, article_style.id)
                if not is_compatible:
                    logger.warning(f"内容类型 {content_type_id} 与风格 {article_style.id} 不兼容")

            # 整合选项
            merged_options = options or {}
            if article_style:
                merged_options["style_info"] = article_style.get_style_summary()
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
            if platform:
                merged_options["platform"] = platform.id
                merged_options["platform_info"] = platform.to_dict()

            # 使用正确的风格ID
            style_id = article_style.id if article_style else style

            # 确保使用正确的方法名
            result = await self.crew.adapt_style(
                article=topic,
                content=content,
                platform=platform_id,
                style=style_id,
                **merged_options
            )
            return result
        except Exception as e:
            raise RuntimeError(f"应用风格失败: {str(e)}")

    async def get_available_styles(self) -> List[Dict[str, Any]]:
        """获取可用的风格列表

        Returns:
            List[Dict[str, Any]]: 风格信息列表
        """
        # 从ContentManager获取所有风格
        all_styles = ContentManager.get_all_article_styles()
        styles_info = []

        for style_id, style in all_styles.items():
            styles_info.append({
                "id": style_id,
                "name": style.name,
                "description": style.description,
                "type": style.type,
                "summary": style.get_style_summary()
            })

        # 同时获取crew中的风格列表（可能包含自定义风格）
        crew_styles = self.crew.get_available_styles()

        # 合并两个列表，确保唯一性
        seen_ids = {style_info["id"] for style_info in styles_info}
        for crew_style in crew_styles:
            if isinstance(crew_style, str) and crew_style not in seen_ids:
                # crew返回的可能只是ID字符串
                style_obj = ContentManager.get_article_style(crew_style)
                if style_obj:
                    styles_info.append({
                        "id": crew_style,
                        "name": style_obj.name,
                        "description": style_obj.description,
                        "type": style_obj.type,
                        "summary": style_obj.get_style_summary()
                    })
                else:
                    styles_info.append({
                        "id": crew_style,
                        "name": crew_style,
                        "description": "",
                        "type": "custom"
                    })
            elif isinstance(crew_style, dict) and crew_style.get("id") not in seen_ids:
                # crew返回的可能是字典格式的风格信息
                styles_info.append(crew_style)

        return styles_info

class ReviewTeamAdapter(BaseTeamAdapter):
    """审核团队适配器"""

    def __init__(self):
        super().__init__()
        self.crew = ReviewCrew()
        self._review_results = {}

    async def initialize(self, **kwargs) -> None:
        """初始化审核团队

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)
        logger.info("审核团队适配器初始化完成")

    async def review_content(
        self,
        topic: Topic,
        content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """审核内容

        Args:
            topic: 话题对象
            content: 待审核内容
            options: 审核选项

        Returns:
            Dict[str, Any]: 审核结果
        """
        try:
            # 获取内容类型
            content_type = None
            content_type_id = None
            if hasattr(topic, 'content_type') and topic.content_type:
                content_type_id = topic.content_type
                content_type = ContentManager.get_content_type(content_type_id)
            elif hasattr(topic, 'categories') and topic.categories:
                # 尝试从第一个分类推断内容类型
                primary_category = topic.categories[0] if topic.categories else None
                if primary_category:
                    content_type = ContentManager.get_content_type_by_category(primary_category)
                    if content_type:
                        content_type_id = content_type.id

            # 获取平台信息
            platform = None
            platform_id = None
            if hasattr(topic, 'platform') and topic.platform:
                platform_id = topic.platform
                platform = ContentManager.get_platform(platform_id)

            # 获取文章风格
            article_style = None
            if platform_id:
                article_style = ContentManager.get_platform_style(platform_id)

            # 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
            if article_style:
                merged_options["style"] = article_style.id
                merged_options["style_info"] = article_style.get_style_summary()
            if platform:
                merged_options["platform"] = platform.id
                merged_options["platform_info"] = platform.to_dict()

            # 确保使用正确的方法名
            result = await self.crew.review_article(
                article=topic,
                content=content,
                platform=platform_id,
                **merged_options
            )
            self._review_results[topic.id] = result
            return result
        except Exception as e:
            raise RuntimeError(f"审核内容失败: {str(e)}")

    async def get_review_result(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """获取审核结果

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Dict[str, Any]]: 审核结果
        """
        return self._review_results.get(topic_id)
