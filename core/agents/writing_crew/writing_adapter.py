"""写作团队适配器模块

为写作团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, Union
import uuid
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.topic import Topic
from core.models.article import Article
from core.agents.writing_crew import WritingCrew

class WritingTeamAdapter(BaseTeamAdapter):
    """写作团队适配器

    职责：
    1. 解析输入的话题信息（从Topic对象或topic_id）
    2. 根据content_type和platform确定写作风格和配置
    3. 调用WritingCrew执行写作
    4. 返回处理后的写作结果

    注意：本层不保存写作结果，只负责参数转换和调用下层
    """

    def __init__(self):
        """初始化写作团队适配器"""
        super().__init__()
        self.crew = None
        self._writing_status = {}  # 用于跟踪写作状态

    async def initialize(self, **kwargs) -> None:
        """初始化写作团队适配器

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)

        if not self.crew:
            self.crew = WritingCrew(verbose=kwargs.get("verbose", True))
            logger.info("写作团队适配器初始化完成")

    async def write_content(
        self,
        topic: Topic,
        research_data: Dict[str, Any],
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """写作内容

        将话题和研究数据转换为WritingCrew需要的格式，
        并根据content_type和platform确定写作风格。

        Args:
            topic: 话题对象
            research_data: 研究资料
            style: 写作风格(可选)
            options: 其他选项

        Returns:
            Dict[str, Any]: 写作结果
        """
        await self.initialize()

        try:
            # 1. 获取话题对应的内容类型
            content_type_id = None
            content_type = None

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

            logger.info(f"解析得到内容类型: {content_type_id or '未指定'}")

            # 2. 获取平台信息
            platform_id = None
            if hasattr(topic, 'platform') and topic.platform:
                platform_id = topic.platform
                logger.info(f"从话题获取平台ID: {platform_id}")

            # 3. 处理文章风格
            style_id = None
            if style:
                # 如果指定了风格，直接使用
                article_style = ContentManager.get_article_style(style)
                if article_style:
                    style_id = article_style.id
                    logger.info(f"使用指定风格: {style_id}")
            elif platform_id:
                # 尝试根据平台获取文章风格
                article_style = ContentManager.get_platform_style(platform_id)
                if article_style:
                    style_id = article_style.id
                    logger.info(f"使用平台风格: {style_id}")

            # 如果有内容类型但没有风格，获取推荐风格
            if content_type_id and not style_id:
                article_style = ContentManager.get_recommended_style_for_content_type(content_type_id)
                if article_style:
                    style_id = article_style.id
                    logger.info(f"为内容类型 {content_type_id} 推荐风格: {style_id}")

            # 检查内容类型和风格是否兼容
            if content_type_id and style_id:
                is_compatible = ContentManager.is_compatible(content_type_id, style_id)
                if not is_compatible:
                    logger.warning(f"内容类型 {content_type_id} 与风格 {style_id} 不兼容，尝试寻找替代方案")
                    # 尝试获取兼容风格
                    article_style = ContentManager.get_recommended_style_for_content_type(content_type_id)
                    if article_style:
                        style_id = article_style.id
                        logger.info(f"使用兼容风格: {style_id}")

            # 4. 整合选项
            merged_options = options or {}
            if content_type:
                merged_options["content_type"] = content_type.id
                merged_options["content_type_info"] = content_type.get_type_summary()
            if article_style:
                merged_options["style"] = article_style.id
                merged_options["style_info"] = article_style.get_style_summary()
            if platform_id:
                platform = ContentManager.get_platform(platform_id)
                if platform:
                    merged_options["platform"] = platform.id
                    merged_options["platform_info"] = platform.to_dict()

            # 5. 创建临时文章对象
            article = Article(
                id=topic.id if hasattr(topic, 'id') else str(uuid.uuid4()),
                title=topic.title if hasattr(topic, 'title') else "未命名",
                topic=topic
            )

            # 记录状态
            if hasattr(topic, 'id'):
                self._writing_status[topic.id] = "processing"

            # 6. 调用WritingCrew执行写作
            result = await self.crew.write_article(
                article=article,
                research_data=research_data,
                platform=platform_id,
                content_type=content_type_id,
                style=style_id,
                **merged_options
            )

            # 7. 更新状态
            if hasattr(topic, 'id'):
                self._writing_status[topic.id] = "completed"

            # 8. 返回写作结果
            return result.to_dict()
        except Exception as e:
            if hasattr(topic, 'id'):
                self._writing_status[topic.id] = "failed"
            raise RuntimeError(f"写作内容失败: {str(e)}")

    async def create_outline(
        self,
        topic_or_text: Union[str, Topic, Dict, Any],
        content_type: Optional[str] = None,
        platform_id: Optional[str] = None,
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """创建内容大纲

        将话题或文本转换为WritingCrew需要的格式，并根据content_type和platform确定大纲风格。

        Args:
            topic_or_text: 话题对象或文本
            content_type: 内容类型(可选)
            platform_id: 平台ID(可选)
            style: 写作风格(可选)
            options: 其他选项

        Returns:
            Dict[str, Any]: 大纲结果
        """
        await self.initialize()

        try:
            # 1. 处理可能的内容类型推断
            final_content_type = content_type
            if not final_content_type and not isinstance(topic_or_text, str):
                if hasattr(topic_or_text, 'content_type') and topic_or_text.content_type:
                    final_content_type = topic_or_text.content_type
                    logger.info(f"从话题获取内容类型: {final_content_type}")
                elif hasattr(topic_or_text, 'categories') and topic_or_text.categories:
                    # 尝试从分类推断内容类型
                    primary_category = topic_or_text.categories[0] if topic_or_text.categories else None
                    if primary_category:
                        content_type_obj = ContentManager.get_content_type_by_category(primary_category)
                        if content_type_obj:
                            final_content_type = content_type_obj.id
                            logger.info(f"从分类推断内容类型: {final_content_type}")

            # 2. 处理风格推断
            final_style = style
            if not final_style and platform_id:
                # 尝试从平台获取风格
                article_style = ContentManager.get_platform_style(platform_id)
                if article_style:
                    final_style = article_style.id
                    logger.info(f"使用平台风格: {final_style}")
            elif not final_style and final_content_type:
                # 尝试获取推荐风格
                article_style = ContentManager.get_recommended_style_for_content_type(final_content_type)
                if article_style:
                    final_style = article_style.id
                    logger.info(f"使用推荐风格: {final_style}")

            # 3. 整合选项
            merged_options = options or {}

            # 记录状态
            topic_id = None
            if not isinstance(topic_or_text, str) and hasattr(topic_or_text, 'id'):
                topic_id = topic_or_text.id
                self._writing_status[topic_id] = "outline_processing"

            # 4. 调用WritingCrew创建大纲
            outline = await self.crew.create_outline(
                topic_or_text=topic_or_text,
                content_type=final_content_type,
                platform_id=platform_id,
                style=final_style,
                options=merged_options
            )

            # 5. 更新状态
            if topic_id:
                self._writing_status[topic_id] = "outline_completed"

            # 6. 返回字典表示
            if hasattr(outline, 'model_dump'):
                return outline.model_dump()
            else:
                return outline.dict()

        except Exception as e:
            topic_id = None
            if not isinstance(topic_or_text, str) and hasattr(topic_or_text, 'id'):
                topic_id = topic_or_text.id
                self._writing_status[topic_id] = "outline_failed"
            raise RuntimeError(f"创建大纲失败: {str(e)}")

    async def expand_content(
        self,
        outline_or_text: Union[str, Dict, Any],
        content_type: Optional[str] = None,
        platform_id: Optional[str] = None,
        style: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """扩展内容

        将大纲转换为WritingCrew需要的格式，并根据content_type和platform确定写作风格。

        Args:
            outline_or_text: 大纲对象或文本
            content_type: 内容类型(可选)
            platform_id: 平台ID(可选)
            style: 写作风格(可选)
            options: 其他选项

        Returns:
            Dict[str, Any]: 扩展结果
        """
        await self.initialize()

        try:
            # 1. 处理可能的内容类型推断
            final_content_type = content_type
            if not final_content_type and not isinstance(outline_or_text, str):
                if hasattr(outline_or_text, 'content_type') and outline_or_text.content_type:
                    final_content_type = outline_or_text.content_type
                    logger.info(f"从大纲获取内容类型: {final_content_type}")

            # 2. 处理风格推断
            final_style = style
            if not final_style and platform_id:
                # 尝试从平台获取风格
                article_style = ContentManager.get_platform_style(platform_id)
                if article_style:
                    final_style = article_style.id
                    logger.info(f"使用平台风格: {final_style}")
            elif not final_style and final_content_type:
                # 尝试获取推荐风格
                article_style = ContentManager.get_recommended_style_for_content_type(final_content_type)
                if article_style:
                    final_style = article_style.id
                    logger.info(f"使用推荐风格: {final_style}")

            # 3. 整合选项
            merged_options = options or {}

            # 记录状态
            topic_id = None
            if not isinstance(outline_or_text, str) and hasattr(outline_or_text, 'topic_id'):
                topic_id = outline_or_text.topic_id
                self._writing_status[topic_id] = "expansion_processing"

            # 4. 调用WritingCrew扩展内容
            result = await self.crew.expand_content(
                outline_or_text=outline_or_text,
                content_type=final_content_type,
                platform_id=platform_id,
                style=final_style,
                options=merged_options
            )

            # 5. 更新状态
            if topic_id:
                self._writing_status[topic_id] = "expansion_completed"

            # 6. 返回扩展结果
            return result

        except Exception as e:
            topic_id = None
            if not isinstance(outline_or_text, str) and hasattr(outline_or_text, 'topic_id'):
                topic_id = outline_or_text.topic_id
                self._writing_status[topic_id] = "expansion_failed"
            raise RuntimeError(f"扩展内容失败: {str(e)}")

    async def get_writing_status(self, topic_id: str) -> str:
        """获取写作状态

        Args:
            topic_id: 话题ID

        Returns:
            str: 写作状态
        """
        return self._writing_status.get(topic_id, "not_found")
