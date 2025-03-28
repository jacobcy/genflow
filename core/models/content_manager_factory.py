"""内容管理器工厂模块

提供内容管理器的工厂类，用于创建各类专用内容管理器。
采用工厂方法模式，将大型ContentManager拆分为多个职责单一的管理器。
"""

from typing import Dict, Any, Type, Optional
from loguru import logger

# 管理器接口定义
class BaseManager:
    """管理器基类接口"""
    _is_initialized: bool = False

    @classmethod
    def initialize(cls) -> None:
        """初始化管理器"""
        if not cls._is_initialized:
            cls._is_initialized = True
            logger.debug(f"{cls.__name__} 初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._is_initialized:
            cls.initialize()


class ContentManagerFactory:
    """内容管理器工厂

    用于创建和获取各种专用内容管理器实例。
    """

    _managers: Dict[str, Type[BaseManager]] = {}
    _use_db: bool = True
    _is_initialized: bool = False

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化工厂

        Args:
            use_db: 是否使用数据库存储，默认为True
        """
        cls._use_db = use_db
        cls._is_initialized = True
        logger.info("ContentManagerFactory 初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保工厂已初始化"""
        if not cls._is_initialized:
            cls.initialize()

    @classmethod
    def register_manager(cls, manager_type: str, manager_class: Type[BaseManager]) -> None:
        """注册管理器类

        Args:
            manager_type: 管理器类型名称
            manager_class: 管理器类
        """
        cls.ensure_initialized()
        cls._managers[manager_type] = manager_class
        logger.debug(f"已注册管理器: {manager_type}")

    @classmethod
    def get_manager(cls, manager_type: str) -> Optional[Type[BaseManager]]:
        """获取指定类型的管理器

        Args:
            manager_type: 管理器类型名称

        Returns:
            Optional[Type[BaseManager]]: 管理器类，如果不存在则返回None
        """
        cls.ensure_initialized()

        # 延迟导入并注册管理器
        if manager_type not in cls._managers:
            try:
                if manager_type == "style":
                    from .managers.style_manager import StyleManager
                    cls.register_manager("style", StyleManager)
                elif manager_type == "platform":
                    from .managers.platform_manager import PlatformManager
                    cls.register_manager("platform", PlatformManager)
                elif manager_type == "content_type":
                    from .managers.content_type_manager import ContentTypeManager
                    cls.register_manager("content_type", ContentTypeManager)
                elif manager_type == "article":
                    from .managers.article_manager import ArticleManager
                    cls.register_manager("article", ArticleManager)
                elif manager_type == "topic":
                    from .managers.topic_manager import TopicManager
                    cls.register_manager("topic", TopicManager)
                elif manager_type == "outline":
                    from .managers.outline_factory import OutlineFactory
                    cls.register_manager("outline", OutlineFactory)
            except ImportError as e:
                logger.error(f"导入管理器 {manager_type} 失败: {str(e)}")
                return None

        # 返回管理器类
        manager_class = cls._managers.get(manager_type)
        if manager_class:
            manager_class.ensure_initialized()

        return manager_class

# 便捷访问方法
def get_style_manager() -> Type[BaseManager]:
    """获取风格管理器"""
    return ContentManagerFactory.get_manager("style")

def get_platform_manager() -> Type[BaseManager]:
    """获取平台管理器"""
    return ContentManagerFactory.get_manager("platform")

def get_content_type_manager() -> Type[BaseManager]:
    """获取内容类型管理器"""
    return ContentManagerFactory.get_manager("content_type")

def get_article_manager() -> Type[BaseManager]:
    """获取文章管理器"""
    return ContentManagerFactory.get_manager("article")

def get_topic_manager() -> Type[BaseManager]:
    """获取话题管理器"""
    return ContentManagerFactory.get_manager("topic")

def get_outline_manager() -> Type[BaseManager]:
    """获取大纲管理器"""
    return ContentManagerFactory.get_manager("outline")
