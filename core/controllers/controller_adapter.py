"""内容生产控制器统一适配层

该模块提供统一的适配器接口，使不同的内容生产控制器具有一致的使用方式。
无论使用哪种底层实现，用户都可以通过相同的接口进行交互。
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any, Union, Callable, Type

from core.models.topic import Topic
from core.models.platform import Platform, get_default_platform
from core.controllers.content_controller import ContentController
from core.controllers.crewai_manager_controller import CrewAIManagerController
from core.controllers.crewai_sequential_controller import CrewAISequentialController
from core.constants.content_types import ALL_CONTENT_TYPES, validate_content_type, get_content_type_from_category
from core.constants.style_types import ALL_STYLE_TYPES, get_style_features
from core.constants.platform_categories import CATEGORY_TAGS

logger = logging.getLogger(__name__)

class BaseContentControllerInterface(ABC):
    """内容生产控制器统一接口"""

    @abstractmethod
    async def initialize(self, platform: Optional[Platform] = None) -> None:
        """初始化控制器

        Args:
            platform: 目标平台
        """
        pass

    @abstractmethod
    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             keywords: Optional[List[str]] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容的统一接口

        Args:
            category: 内容类别
            topic: 指定话题（如果已有）
            style: 写作风格
            keywords: 关键词列表
            content_type: 内容类型（如"新闻"、"论文"、"快讯"、"研究报告"等）
            platform: 目标平台
            options: 控制器特定的额外选项

        Returns:
            Dict: 生产结果
        """
        pass

    @abstractmethod
    def get_progress(self) -> Dict:
        """获取生产进度

        Returns:
            Dict: 进度信息
        """
        pass


class ContentControllerAdapter(BaseContentControllerInterface):
    """自定义顺序流程控制器适配器"""

    def __init__(self, **kwargs):
        """初始化适配器"""
        self.controller = ContentController()

    async def initialize(self, platform: Optional[Platform] = None) -> None:
        """初始化控制器

        Args:
            platform: 目标平台
        """
        await self.controller.initialize(platform=platform)

    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             keywords: Optional[List[str]] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            topic: 指定话题
            style: 写作风格（此控制器通过research_crew和writing_crew读取）
            keywords: 关键词列表（此控制器将其转换为topic相关内容）
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）
            platform: 目标平台
            options: 其他选项

        Returns:
            Dict: 生产结果
        """
        # 提取ContentController特有的参数
        options = options or {}
        topic_count = options.get("topic_count", 1)
        progress_callback = options.get("progress_callback", None)
        mode = options.get("mode", "human")
        auto_stages = options.get("auto_stages", None)

        # 关键词处理 - 如果有topic但没有description，使用keywords作为描述
        if topic and not getattr(topic, "description", None) and keywords:
            topic.description = f"关于{', '.join(keywords)}的内容"

        # 如果有keywords但没有topic，可以创建一个topic对象
        if not topic and keywords and category:
            topic = Topic(
                name=category,
                description=f"关于{', '.join(keywords)}的{category}内容"
            )

        # 处理内容类型 - 添加到topic的metadata或description中
        if content_type and topic:
            if not hasattr(topic, "metadata"):
                topic.metadata = {}
            topic.metadata["content_type"] = content_type

            # 如果有description，在描述中添加内容类型
            if hasattr(topic, "description") and topic.description:
                topic.description = f"{topic.description}，输出格式为{content_type}"

        # 如果有style，也添加到topic的metadata中
        if style and topic and hasattr(topic, "metadata"):
            topic.metadata["style"] = style

        # 调用原生方法
        result = await self.controller.produce_content(
            topic=topic,
            category=category,
            platform=platform,
            topic_count=topic_count,
            progress_callback=progress_callback,
            mode=mode,
            auto_stages=auto_stages
        )

        return result

    def get_progress(self) -> Dict:
        """获取生产进度"""
        return self.controller.get_progress()


class CrewAIManagerControllerAdapter(BaseContentControllerInterface):
    """CrewAI层级流程控制器适配器"""

    def __init__(self, model_name="gpt-4", **kwargs):
        """初始化适配器"""
        self.controller = CrewAIManagerController(model_name=model_name)

    async def initialize(self, platform: Optional[Platform] = None) -> None:
        """初始化控制器

        Args:
            platform: 目标平台
        """
        await self.controller.initialize(platform=platform)

    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             keywords: Optional[List[str]] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            topic: 指定话题（此控制器不使用此参数，但从中提取category）
            style: 写作风格
            keywords: 关键词列表
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）
            platform: 目标平台（此控制器仅记录平台名称）
            options: 其他选项（不使用）

        Returns:
            Dict: 生产结果
        """
        # 如果没有提供category但有topic，从topic提取
        if not category and topic:
            category = getattr(topic, "name", None) or getattr(topic, "category", None) or "通用"

        # 处理内容类型 - 结合category或使用task_context
        extended_category = category
        if content_type:
            extended_category = f"{category} ({content_type})"

            # 将内容类型保存到控制器状态，以便任务创建时使用
            if hasattr(self.controller, "state"):
                self.controller.state.content_type = content_type

        # 使用options处理额外的控制器配置
        options = options or {}

        # 调用原生方法
        result = await self.controller.produce_content(
            category=extended_category,
            style=style,
            keywords=keywords
        )

        # 将内容类型添加到结果中
        if content_type and isinstance(result, dict):
            result["content_type"] = content_type

        return result

    def get_progress(self) -> Dict:
        """获取生产进度"""
        return self.controller.get_progress()


class CrewAISequentialControllerAdapter(BaseContentControllerInterface):
    """CrewAI标准顺序流程控制器适配器"""

    def __init__(self, model_name="gpt-4", **kwargs):
        """初始化适配器"""
        self.controller = CrewAISequentialController(model_name=model_name)

    async def initialize(self, platform: Optional[Platform] = None) -> None:
        """初始化控制器

        Args:
            platform: 目标平台
        """
        await self.controller.initialize(platform=platform)

    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             keywords: Optional[List[str]] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            topic: 指定话题（此控制器不使用此参数，但从中提取category）
            style: 写作风格
            keywords: 关键词列表
            content_type: 内容类型（如"新闻"、"论文"、"快讯"等）
            platform: 目标平台（此控制器仅记录平台名称）
            options: 其他选项（不使用）

        Returns:
            Dict: 生产结果
        """
        # 如果没有提供category但有topic，从topic提取
        if not category and topic:
            category = getattr(topic, "name", None) or getattr(topic, "category", None) or "通用"

        # 处理内容类型 - 结合category或使用task_context
        extended_category = category
        if content_type:
            extended_category = f"{category} ({content_type})"

            # 将内容类型保存到控制器状态，以便任务创建时使用
            if hasattr(self.controller, "state"):
                self.controller.state.content_type = content_type

            # 修改风格描述，包含内容类型
            if style:
                style = f"{style}风格的{content_type}"
            else:
                style = f"{content_type}风格"

        # 使用options处理额外的控制器配置
        options = options or {}

        # 调用原生方法
        result = await self.controller.produce_content(
            category=extended_category,
            style=style,
            keywords=keywords
        )

        # 将内容类型添加到结果中
        if content_type and isinstance(result, dict):
            result["content_type"] = content_type

        return result

    def get_progress(self) -> Dict:
        """获取生产进度"""
        return self.controller.get_progress()


class ContentControllerFactory:
    """内容生产控制器工厂

    提供统一的方式创建和获取不同类型的内容生产控制器。
    """

    # 控制器类型映射
    CONTROLLER_TYPES = {
        "custom_sequential": ContentControllerAdapter,
        "crewai_manager": CrewAIManagerControllerAdapter,
        "crewai_sequential": CrewAISequentialControllerAdapter
    }

    @staticmethod
    async def create_controller(controller_type: str, **kwargs) -> BaseContentControllerInterface:
        """创建指定类型的控制器

        Args:
            controller_type: 控制器类型，可选值包括：
                - "custom_sequential": 自定义顺序流程
                - "crewai_manager": CrewAI层级流程
                - "crewai_sequential": CrewAI标准顺序流程
            **kwargs: 传递给控制器的其他参数

        Returns:
            BaseContentControllerInterface: 统一接口的控制器实例

        Raises:
            ValueError: 如果指定了未知的控制器类型
        """
        if controller_type not in ContentControllerFactory.CONTROLLER_TYPES:
            raise ValueError(f"未知的控制器类型: {controller_type}，可用类型: {list(ContentControllerFactory.CONTROLLER_TYPES.keys())}")

        # 创建控制器适配器
        controller_adapter = ContentControllerFactory.CONTROLLER_TYPES[controller_type](**kwargs)

        # 初始化控制器
        platform = kwargs.get("platform", None)
        await controller_adapter.initialize(platform=platform)

        return controller_adapter

    @staticmethod
    def is_valid_category(category: str) -> bool:
        """检查类别是否为标准类别

        Args:
            category: 要检查的类别

        Returns:
            bool: 类别是否为标准类别
        """
        return category in CATEGORY_TAGS

    @staticmethod
    def is_valid_content_type(content_type: str) -> bool:
        """检查内容类型是否有效

        Args:
            content_type: 要检查的内容类型

        Returns:
            bool: 内容类型是否有效
        """
        return validate_content_type(content_type)

    @staticmethod
    def is_valid_style(style: str) -> bool:
        """检查风格是否为标准风格

        Args:
            style: 要检查的风格

        Returns:
            bool: 风格是否为标准风格
        """
        return style in ALL_STYLE_TYPES


# 使用示例
async def example_usage():
    """示例：使用统一接口创建和使用内容生产控制器"""
    # 创建平台对象
    platform = Platform(
        id="zhihu",
        name="知乎",
        url="https://www.zhihu.com",
        content_rules={
            "min_words": 1000,
            "max_words": 5000,
            "allowed_tags": ["Python", "编程", "技术"]
        }
    )

    # 使用工厂创建控制器（自定义顺序流程）
    controller1 = await ContentControllerFactory.create_controller(
        "custom_sequential",
        platform=platform
    )

    # 生产内容
    result1 = await controller1.produce_content(
        category="技术",
        keywords=["Python", "编程"],
        content_type="教程",  # 指定内容类型
        platform=platform,
        options={
            "topic_count": 1,
            "mode": "auto"
        }
    )
    print(f"自定义顺序流程控制器结果: {result1.get('status')}")

    # 使用工厂创建控制器（CrewAI层级流程）
    controller2 = await ContentControllerFactory.create_controller(
        "crewai_manager",
        model_name="gpt-4",
        platform=platform
    )

    # 生产内容
    result2 = await controller2.produce_content(
        category="技术",
        style="专业",
        keywords=["Python", "编程"],
        content_type="研究报告"  # 指定内容类型
    )
    print(f"CrewAI层级流程控制器结果: {result2.get('status')}")

    # 获取进度
    progress = controller2.get_progress()
    print(f"进度: {progress}")


if __name__ == "__main__":
    asyncio.run(example_usage())
