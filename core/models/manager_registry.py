"""管理器注册中心

提供获取各管理器的统一入口
"""

from typing import Type, Optional, cast
from loguru import logger

from .simple_content_manager import SimpleContentManager
from .content_manager import ContentManager
from .config_manager import ConfigManager
from .operation_manager import OperationManager


class ManagerRegistry:
    """管理器注册中心

    提供获取各管理器的统一入口，确保单例模式
    """

    _initialized = False
    _simple_content_manager: Optional[Type[SimpleContentManager]] = None
    _content_manager: Optional[Type[ContentManager]] = None
    _config_manager: Optional[Type[ConfigManager]] = None
    _operation_manager: Optional[Type[OperationManager]] = None

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化管理器注册中心

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        # 初始化各管理器
        cls._simple_content_manager = SimpleContentManager
        cls._simple_content_manager.initialize(use_db)

        cls._content_manager = ContentManager
        cls._content_manager.initialize(use_db)

        cls._config_manager = ConfigManager
        cls._config_manager.initialize(use_db)

        cls._operation_manager = OperationManager
        cls._operation_manager.initialize(use_db)

        cls._initialized = True
        logger.info("管理器注册中心初始化完成")

    @classmethod
    def get_simple_content_manager(cls) -> Type[SimpleContentManager]:
        """获取简单内容管理器

        Returns:
            Type[SimpleContentManager]: 简单内容管理器
        """
        if not cls._initialized:
            cls.initialize()
        return cast(Type[SimpleContentManager], cls._simple_content_manager)

    @classmethod
    def get_content_manager(cls) -> Type[ContentManager]:
        """获取持久内容管理器

        Returns:
            Type[ContentManager]: 持久内容管理器
        """
        if not cls._initialized:
            cls.initialize()
        return cast(Type[ContentManager], cls._content_manager)

    @classmethod
    def get_config_manager(cls) -> Type[ConfigManager]:
        """获取配置管理器

        Returns:
            Type[ConfigManager]: 配置管理器
        """
        if not cls._initialized:
            cls.initialize()
        return cast(Type[ConfigManager], cls._config_manager)

    @classmethod
    def get_operation_manager(cls) -> Type[OperationManager]:
        """获取操作管理器

        Returns:
            Type[OperationManager]: 操作管理器
        """
        if not cls._initialized:
            cls.initialize()
        return cast(Type[OperationManager], cls._operation_manager)
