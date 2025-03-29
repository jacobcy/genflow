"""风格团队适配器模块

为风格团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, Union
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.article.basic_article import BasicArticle, Article
from core.agents.style_crew import StyleCrew

class StyleTeamAdapter(BaseTeamAdapter):
    """风格团队适配器

    职责：
    1. 解析输入的内容信息（从outline_id或文本内容）
    2. 根据style_id或style_type确定风格配置
    3. 调用StyleCrew执行风格适配
    4. 返回BasicArticle或Article对象

    注意：本层不保存风格处理结果，只负责参数转换和调用下层
    """

    def __init__(self):
        """初始化风格团队适配器"""
        super().__init__()
        self.crew = None
        self._style_status = {}  # 用于跟踪风格处理状态

    async def initialize(self, **kwargs) -> None:
        """初始化风格团队适配器

        Args:
            **kwargs: 初始化参数
        """
        await super().initialize(**kwargs)

        if not self.crew:
            self.crew = StyleCrew(verbose=kwargs.get("verbose", True))
            logger.info("风格团队初始化完成")

    async def adapt_style(
        self,
        content: Union[str, Dict, Any],
        platform_id: Optional[str] = None,
        style_name: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[BasicArticle, Article]:
        """适配内容风格

        将所有输入内容统一转换为BasicArticle对象，然后提交给StyleCrew进行风格处理。

        Args:
            content: 需要调整风格的内容（文本、ID、outline对象或article对象）
            platform_id: 目标平台ID
            style_name: 目标风格名称或描述文本
            options: 其他选项

        Returns:
            Union[BasicArticle, Article]: 风格调整后的文章对象
        """
        await self.initialize()

        try:
            # 1. 统一将内容转换为BasicArticle对象
            article_obj = self._convert_to_basic_article(content)
            if not article_obj:
                raise ValueError(f"无法将内容转换为BasicArticle对象: {content}")

            content_id = article_obj.id

            # 2. 获取风格对象
            style_obj = None

            # 优先使用提供的风格名称或描述
            if style_name:
                style_obj = ContentManager.get_or_create_style(style_name, options)
                logger.info(f"使用风格: {style_obj.name}")
            # 其次尝试根据平台获取风格
            elif platform_id:
                style_obj = ContentManager.get_platform_style(platform_id)
                if style_obj:
                    logger.info(f"使用平台 {platform_id} 的风格: {style_obj.name}")

            # 如果以上都没有，使用默认风格
            if not style_obj:
                from core.models.style.article_style import get_default_style
                style_obj = get_default_style()
                logger.info("使用默认风格")

            # 3. 转换为风格配置
            style_config = style_obj.to_style_config()

            # 如果提供了平台ID但没有在风格中指定，添加到配置中
            if platform_id and "platform_id" not in style_config:
                style_config["platform_id"] = platform_id

            # 4. 准备平台信息
            platform_info = self._prepare_platform_info(platform_id, options)

            # 5. 记录状态
            if content_id:
                self._style_status[content_id] = "processing"

            # 6. 准备选项
            merged_options = self._prepare_options(options, style_config)

            # 7. 调用StyleCrew执行风格适配
            result = await self.crew.style_text(
                article=article_obj,
                style_config=style_config,
                platform_info=platform_info,
                options=merged_options
            )

            # 8. 记录状态
            if content_id:
                self._style_status[content_id] = "completed"

            # 9. 返回结果
            if hasattr(result, 'to_article') and callable(getattr(result, 'to_article')):
                return result.to_article(content_id)
            return result.final_article if hasattr(result, 'final_article') else result

        except Exception as e:
            if content_id:
                self._style_status[content_id] = "failed"
            raise RuntimeError(f"风格适配失败: {str(e)}")

    def _prepare_platform_info(self, platform_id: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """准备平台信息

        Args:
            platform_id: 平台ID
            options: 选项

        Returns:
            Dict[str, Any]: 平台信息
        """
        # 默认平台信息
        platform_info = {
            "platform_id": platform_id,
            "platform_name": platform_id
        }

        # 尝试获取平台详细信息
        if platform_id:
            platform = ContentManager.get_platform(platform_id)
            if platform:
                platform_info["platform_name"] = platform.name
                if hasattr(platform, "description"):
                    platform_info["platform_description"] = platform.description
                if hasattr(platform, "platform_type"):
                    platform_info["platform_type"] = platform.platform_type

        # 合并用户提供的平台信息
        if options and isinstance(options, dict):
            for key, value in options.items():
                if key.startswith("platform_") and key not in platform_info:
                    platform_info[key] = value

        return platform_info

    def _convert_to_basic_article(self, content) -> Optional[BasicArticle]:
        """将各种格式的内容统一转换为BasicArticle对象

        Args:
            content: 输入内容（文本、ID、Outline对象或Article对象）

        Returns:
            Optional[BasicArticle]: 转换后的BasicArticle对象，如果无法转换则返回None
        """
        # 1. 如果已经是BasicArticle对象，直接返回
        if isinstance(content, BasicArticle):
            return content

        # 2. 如果是Article对象，转换为BasicArticle
        if hasattr(content, 'to_basic_article') and callable(getattr(content, 'to_basic_article')):
            return content.to_basic_article()

        # 3. 处理字符串类型
        if isinstance(content, str):
            # a. 检查是否是outline_id
            if content.startswith("outline_") or content.isdigit():
                try:
                    outline = ContentManager.get_outline(content)
                    if outline:
                        # 调用outline的to_basic_article方法
                        return outline.to_basic_article()
                except Exception as e:
                    logger.error(f"获取或转换outline失败: {str(e)}")

            # b. 将纯文本作为内容创建BasicArticle
            return BasicArticle(
                title="临时文章",
                content=content
            )

        # 4. 处理字典类型
        if isinstance(content, dict):
            if "content" in content:
                title = content.get("title", "临时文章")
                content_id = content.get("id")
                return BasicArticle(
                    id=content_id,
                    title=title,
                    content=content["content"]
                )

        # 5. 尝试提取内容属性
        if hasattr(content, 'content'):
            title = getattr(content, 'title', "临时文章")
            content_id = getattr(content, 'id', None)
            return BasicArticle(
                id=content_id,
                title=title,
                content=content.content
            )

        # 无法转换时
        logger.warning(f"无法将内容转换为BasicArticle: {type(content)}")
        return None

    def _prepare_options(self, options, style_config) -> Dict[str, Any]:
        """准备完整的选项

        Args:
            options: 用户提供的选项
            style_config: 风格配置

        Returns:
            Dict[str, Any]: 合并后的选项
        """
        merged_options = options or {}

        # 确保不覆盖用户提供的选项
        for key, value in style_config.items():
            if key not in merged_options:
                merged_options[key] = value

        return merged_options

    async def analyze_platform(
        self,
        platform_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """分析平台风格特点

        Args:
            platform_id: 平台ID
            options: 其他选项

        Returns:
            Dict[str, Any]: 平台分析结果
        """
        await self.initialize()

        try:
            # 准备平台信息
            platform_info = self._prepare_platform_info(platform_id, options)

            # 准备选项
            merged_options = options or {}

            # 调用StyleCrew进行平台分析
            platform_analysis = await self.crew.analyze_platform(
                platform_info=platform_info,
                options=merged_options
            )

            return {
                "platform_id": platform_id,
                "platform_name": platform_info.get("platform_name", "未知平台"),
                "analysis": platform_analysis,
                "timestamp": platform_analysis.get("timestamp", "")
            }

        except Exception as e:
            raise RuntimeError(f"平台分析失败: {str(e)}")

    async def get_style_status(self, content_id: str) -> str:
        """获取风格处理状态

        Args:
            content_id: 内容ID

        Returns:
            str: 风格处理状态
        """
        return self._style_status.get(content_id, "not_found")
