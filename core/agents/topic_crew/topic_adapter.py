"""选题团队适配器模块

为选题团队提供统一的接口适配层，处理参数转换和错误处理。
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from core.controllers.base_adapter import BaseTeamAdapter
from core.models.content_manager import ContentManager
from core.models.topic import Topic
from core.agents.topic_crew import TopicCrew

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
