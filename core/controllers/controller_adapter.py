"""内容生产控制器统一适配层

该模块提供统一的适配器接口，使不同的内容生产控制器具有一致的使用方式。
无论使用哪种底层实现，用户都可以通过相同的接口进行交互。
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any, Union, Callable, Type

from core.models.topic.topic import Topic
from core.models.article.article import Article
from core.models.platform.platform import Platform, get_default_platform
from core.controllers.content_controller import ContentController
from core.controllers.crewai_hierarchical_controller import CrewAIManagerController
from core.controllers.crewai_sequential_controller import CrewAISequentialController
from core.tools.trending_tools.platform_categories import CATEGORY_TAGS

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
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容的统一接口

        Args:
            category: 内容类别
            topic: 指定话题（如果已有）
            style: 写作风格
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

    @abstractmethod
    def cancel_production(self) -> Dict:
        """取消内容生产

        Returns:
            Dict: 取消操作结果
        """
        pass

class BaseControllerAdapter(BaseContentControllerInterface):
    """基础控制器适配器，处理共同的逻辑"""

    def __init__(self, controller_class, **kwargs):
        """初始化基础适配器

        Args:
            controller_class: 具体控制器类
            **kwargs: 传递给控制器的参数
        """
        self.controller = controller_class(**kwargs)

    async def initialize(self, platform: Optional[Platform] = None) -> None:
        """初始化控制器

        Args:
            platform: 目标平台
        """
        await self.controller.initialize(platform=platform)

    def get_progress(self) -> Dict:
        """获取生产进度"""
        return self.controller.get_progress()

    def cancel_production(self) -> Dict:
        """取消内容生产"""
        if hasattr(self.controller, "cancel_production"):
            return self.controller.cancel_production()
        return {"status": "unsupported", "message": "此控制器不支持取消操作"}

    def _process_category(self, category: Optional[str], topic: Optional[Topic]) -> str:
        """处理类别信息

        Args:
            category: 类别
            topic: 话题对象

        Returns:
            str: 处理后的类别
        """
        if not category and topic:
            return getattr(topic, "name", None) or getattr(topic, "category", None) or "通用"
        return category or "通用"

    def _process_content_type(self, category: str, content_type: Optional[str]) -> str:
        """处理内容类型

        Args:
            category: 类别
            content_type: 内容类型

        Returns:
            str: 处理后的类别（可能包含内容类型信息）
        """
        if content_type:
            if hasattr(self.controller, "state"):
                self.controller.state.content_type = content_type
            return f"{category} ({content_type})"
        return category

    def _process_style(self, style: Optional[str], content_type: Optional[str]) -> str:
        """处理写作风格

        Args:
            style: 原始风格
            content_type: 内容类型

        Returns:
            str: 处理后的风格
        """
        if not content_type:
            return style or "neutral"

        if style:
            return f"{style}风格的{content_type}"
        return f"{content_type}风格"

    def _process_topic(self, topic: Optional[Topic], category: Optional[str],
                      content_type: Optional[str], style: Optional[str]) -> Optional[Topic]:
        """处理话题对象

        Args:
            topic: 原始话题对象
            category: 类别
            content_type: 内容类型
            style: 写作风格

        Returns:
            Optional[Topic]: 处理后的话题对象
        """
        if topic:
            if not hasattr(topic, "metadata"):
                topic.metadata = {}
            if content_type:
                topic.metadata["content_type"] = content_type
            if style:
                topic.metadata["style"] = style

        return topic

    def _prepare_article(self, article: Optional[Article], topic: Optional[Topic],
                       content_type: Optional[str], style: Optional[str]) -> Optional[Article]:
        """准备文章对象

        根据提供的参数创建或更新文章对象

        Args:
            article: 原始文章对象
            topic: 话题对象
            content_type: 内容类型
            style: 写作风格

        Returns:
            Optional[Article]: 处理后的文章对象
        """
        if article:
            # 更新现有文章
            if topic and not article.topic_id:
                article.topic_id = getattr(topic, "id", None)
                article.topic = topic

            if content_type and not getattr(article, "content_type", None):
                article.content_type = content_type

            if style and not getattr(article, "style", None):
                # 根据文章类的实现方式设置风格
                if hasattr(article, "style"):
                    if isinstance(article.style, dict):
                        article.style["tone"] = style
                    elif hasattr(article.style, "tone"):
                        article.style.tone = style
                    else:
                        article.style = style
                else:
                    # 如果没有style属性，可以添加到metadata
                    if not hasattr(article, "metadata"):
                        article.metadata = {}
                    article.metadata["style"] = style

            return article
        elif topic:
            # 根据话题创建新文章
            from uuid import uuid4

            # 创建基本文章对象
            new_article = Article(
                id=str(uuid4()),
                topic_id=getattr(topic, "id", None),
                title=getattr(topic, "title", "未命名文章"),
                summary=getattr(topic, "summary", ""),
                content="",
                status="pending"
            )

            # 设置话题引用
            new_article.topic = topic

            # 设置内容类型和风格
            if content_type:
                new_article.content_type = content_type

            if style:
                # 根据文章类的实现设置风格
                if hasattr(new_article, "style"):
                    if isinstance(new_article.style, dict):
                        new_article.style["tone"] = style
                    elif hasattr(new_article.style, "tone"):
                        new_article.style.tone = style
                    else:
                        new_article.style = style
                else:
                    # 如果没有style属性，添加到metadata
                    if not hasattr(new_article, "metadata"):
                        new_article.metadata = {}
                    new_article.metadata["style"] = style

            return new_article

        return None

class ContentControllerAdapter(BaseControllerAdapter):
    """内容控制器适配器

    这是一个特殊的适配器，用于处理 ContentController 的特定功能，
    包括自动化模式设置和阶段控制。
    """

    def __init__(self, **kwargs):
        """初始化适配器

        Args:
            **kwargs: 配置参数
                - mode: 生产模式，可选 'auto'(全自动), 'human'(全人工辅助), 'mixed'(混合模式)
                - auto_stages: 当mode为'mixed'时，指定自动执行的阶段列表
        """
        from core.controllers.content_controller import ContentController
        super().__init__(ContentController, **kwargs)

        # 设置默认模式
        self.mode = kwargs.get("mode", "human")
        self.auto_stages = kwargs.get("auto_stages", None)

        # 阶段映射
        from core.models.progress import ProductionStage
        self.stage_map = {
            "topic_discovery": ProductionStage.TOPIC_DISCOVERY,
            "topic_research": ProductionStage.TOPIC_RESEARCH,
            "article_writing": ProductionStage.ARTICLE_WRITING,
            "style_adaptation": ProductionStage.STYLE_ADAPTATION,
            "article_review": ProductionStage.ARTICLE_REVIEW
        }

        # 初始化时设置模式
        self._set_controller_mode()

    def _set_controller_mode(self):
        """设置控制器的生产模式"""
        if self.auto_stages and self.mode == 'mixed':
            auto_stages_enum = [
                self.stage_map[s]
                for s in self.auto_stages
                if s in self.stage_map
            ]
            self.controller.set_auto_mode(self.mode, auto_stages_enum)
        else:
            self.controller.set_auto_mode(self.mode)

    def set_mode(self, mode: str, auto_stages: Optional[List[str]] = None):
        """设置生产模式

        Args:
            mode: 'auto', 'human', 或 'mixed'
            auto_stages: 在 mixed 模式下要自动执行的阶段列表
        """
        self.mode = mode
        self.auto_stages = auto_stages
        self._set_controller_mode()

    async def produce_content(self,
                            category: Optional[str] = None,
                            topic: Optional[Topic] = None,
                            style: Optional[str] = None,
                            content_type: Optional[str] = None,
                            platform: Optional[Platform] = None,
                            options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        特殊处理：
        1. 确保模式设置正确传递给控制器
        2. 处理自动化阶段的设置

        Args:
            category: 话题类别
            topic: 指定话题对象
            style: 写作风格
            content_type: 内容类型
            platform: 目标平台
            options: 其他选项，包括：
                - topic_count: 话题数量（当topic不提供时使用）
                - progress_callback: 进度回调函数
                - mode: 生产模式，可选 'auto', 'human', 'mixed'
                - auto_stages: mixed模式下的自动执行阶段列表
                - article: 文章对象（可选）

        Returns:
            Dict: 生产结果
        """
        # 处理 options
        options = options or {}

        # 如果在 options 中指定了新的模式，更新适配器的模式设置
        if "mode" in options:
            self.set_mode(
                options["mode"],
                options.get("auto_stages", self.auto_stages)
            )
        else:
            # 使用适配器当前的模式设置
            options["mode"] = self.mode
            if self.auto_stages and self.mode == "mixed":
                options["auto_stages"] = self.auto_stages

        # 处理文章对象
        article = options.get("article")
        if article:
            # 确保文章对象包含必要的信息
            article = self._prepare_article(article, topic, content_type, style)

        # 调用控制器的生产方法
        result = await self.controller.produce_content(
            category=category,
            topic=topic,
            style=style,
            content_type=content_type,
            platform=platform,
            options=options
        )

        return result

    def get_available_modes(self) -> Dict[str, Any]:
        """获取可用的模式和阶段信息

        Returns:
            Dict[str, Any]: 包含可用模式、阶段和当前设置的信息
        """
        return {
            "modes": ["auto", "human", "mixed"],
            "stages": list(self.stage_map.keys()),
            "current_mode": self.mode,
            "current_auto_stages": self.auto_stages
        }

    def get_progress(self) -> Dict:
        """获取当前进度

        Returns:
            Dict: 进度信息
        """
        return self.controller.get_progress()

    def pause_production(self):
        """暂停生产"""
        if hasattr(self.controller, "pause_production"):
            return self.controller.pause_production()
        return {"status": "unsupported", "message": "此控制器不支持暂停操作"}

    def resume_production(self):
        """恢复生产"""
        if hasattr(self.controller, "resume_production"):
            return self.controller.resume_production()
        return {"status": "unsupported", "message": "此控制器不支持恢复操作"}

    def cancel_production(self) -> Dict:
        """取消内容生产

        自定义流程没有显式的取消方法，尝试使用暂停

        Returns:
            Dict: 取消操作结果
        """
        if hasattr(self.controller, "pause_production"):
            result = self.controller.pause_production()
            return {"status": "cancelled" if result.get("status") == "paused" else "failed",
                   "message": "内容生产已取消"}
        return {"status": "unsupported", "message": "此控制器不支持取消操作"}


class CrewAIManagerControllerAdapter(BaseControllerAdapter):
    """CrewAI 管理器控制器适配器"""

    def __init__(self, **kwargs):
        """初始化适配器"""
        super().__init__(CrewAIManagerController, **kwargs)

    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            topic: 指定话题
            style: 写作风格
            content_type: 内容类型
            platform: 目标平台
            options: 其他选项，包括：
                - article: 文章对象（可选）

        Returns:
            Dict: 生产结果
        """
        # 处理options
        options = options or {}

        # 处理文章对象
        article = options.get("article")
        if article:
            # 确保文章对象包含必要的信息
            article = self._prepare_article(article, topic, content_type, style)

        # 处理类别
        processed_category = self._process_category(category, topic)

        # 处理内容类型
        if content_type and hasattr(self.controller, "state"):
            self.controller.state.content_type = content_type

        # 直接调用控制器实现
        result = await self.controller.produce_content(
            category=processed_category,
            style=style,
            article=article
        )

        return result


class CrewAISequentialControllerAdapter(BaseControllerAdapter):
    """CrewAI 顺序控制器适配器"""

    def __init__(self, **kwargs):
        """初始化适配器"""
        super().__init__(CrewAISequentialController, **kwargs)

    async def produce_content(self,
                             category: Optional[str] = None,
                             topic: Optional[Topic] = None,
                             style: Optional[str] = None,
                             content_type: Optional[str] = None,
                             platform: Optional[Platform] = None,
                             options: Optional[Dict[str, Any]] = None) -> Dict:
        """生产内容

        Args:
            category: 内容类别
            topic: 指定话题
            style: 写作风格
            content_type: 内容类型
            platform: 目标平台
            options: 其他选项，包括：
                - article: 文章对象（可选）

        Returns:
            Dict: 生产结果
        """
        # 处理options
        options = options or {}

        # 处理文章对象
        article = options.get("article")
        if article:
            # 确保文章对象包含必要的信息
            article = self._prepare_article(article, topic, content_type, style)

        # 处理类别
        processed_category = self._process_category(category, topic)

        # 处理内容类型
        if content_type and hasattr(self.controller, "state"):
            self.controller.state.content_type = content_type

        # 直接调用控制器实现
        result = await self.controller.produce_content(
            category=processed_category,
            style=style,
            article=article
        )

        return result


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
            **kwargs: 传递给控制器的其他参数，可包括：
                - model_name: 模型名称（适用于CrewAI控制器）
                - platform: 目标平台
                - mode: 自定义控制器的模式（auto/human/mixed）
                - auto_stages: 自定义控制器的自动阶段列表

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
        # 此处需要导入内容类型验证函数
        # 考虑添加导入或实现验证逻辑
        return True  # 临时返回，实际应根据系统定义验证

    @staticmethod
    def is_valid_style(style: str) -> bool:
        """检查风格是否为标准风格

        Args:
            style: 要检查的风格

        Returns:
            bool: 风格是否为标准风格
        """
        # 此处需要导入或定义标准风格列表
        # 考虑添加导入或实现验证逻辑
        return True  # 临时返回，实际应根据系统定义验证


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

    # 创建文章对象
    article = Article(
        id="example-article-1",
        title="示例文章",
        summary="这是一篇用于测试的示例文章",
        status="pending"
    )

    # 使用工厂创建控制器（自定义顺序流程）
    controller1 = await ContentControllerFactory.create_controller(
        "custom_sequential",
        platform=platform
    )

    # 生产内容
    result1 = await controller1.produce_content(
        category="技术",
        content_type="教程",  # 指定内容类型
        platform=platform,
        options={
            "topic_count": 1,
            "mode": "auto",
            "article": article
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
        content_type="研究报告",  # 指定内容类型
        options={
            "article": article
        }
    )
    print(f"CrewAI层级流程控制器结果: {result2.get('status')}")

    # 测试取消功能
    cancel_result = controller2.cancel_production()
    print(f"取消结果: {cancel_result}")

    # 获取进度
    progress = controller2.get_progress()
    print(f"进度: {progress}")


if __name__ == "__main__":
    asyncio.run(example_usage())
