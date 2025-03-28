"""审核团队适配器模块

为审核团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, Union
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.topic import Topic
from core.agents.review_crew import ReviewCrew

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

    async def review_article(
        self,
        article: Union[Dict[str, Any], Any],
        platform_id: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """审核文章

        Args:
            article: 文章对象
            platform_id: 平台ID
            options: 其他选项

        Returns:
            Dict[str, Any]: 审核结果
        """
        try:
            # 获取平台信息
            platform = None
            if platform_id:
                platform = ContentManager.get_platform(platform_id)
            elif hasattr(article, 'platform') and article.platform:
                platform_id = article.platform
                platform = ContentManager.get_platform(platform_id)

            # 整合选项
            merged_options = options or {}
            if platform:
                merged_options["platform"] = platform.id
                merged_options["platform_info"] = platform.to_dict()

            # 调用底层方法
            result = await self.crew.review_article(
                article=article,
                platform_id=platform_id,
                **merged_options
            )

            # 记录审核结果
            article_id = getattr(article, 'id', None) if not isinstance(article, dict) else article.get('id')
            if article_id:
                self._review_results[article_id] = result

            return result
        except Exception as e:
            raise RuntimeError(f"审核文章失败: {str(e)}")

    async def get_review_result(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """获取审核结果

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Dict[str, Any]]: 审核结果
        """
        return self._review_results.get(topic_id)
