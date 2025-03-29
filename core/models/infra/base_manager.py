"""基础管理器

所有管理器类的基类，定义了通用接口和属性
"""

from typing import ClassVar
from abc import ABC, abstractmethod
from loguru import logger


class BaseManager(ABC):
    """基础管理器

    所有管理器类的抽象基类，定义了通用接口和属性

    由于这是一个抽象基类，所有子类需要实现其接口，或者使用默认实现
    """

    # 类变量
    _initialized: ClassVar[bool] = False
    _use_db: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化

        如果管理器未初始化，则调用initialize方法。
        此方法在每次调用管理器方法之前都应该被调用，以确保管理器处于初始化状态。
        """
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化管理器

        执行管理器的初始化操作，如加载数据、连接数据库等。
        子类应该覆盖此方法以实现自己的初始化逻辑。
        """
        cls._initialized = True
        logger.debug(f"{cls.__name__} 已初始化")

    @classmethod
    def use_db(cls) -> bool:
        """返回管理器是否使用数据库

        Returns:
            bool: 是否使用数据库
        """
        return cls._use_db

    @classmethod
    def set_use_db(cls, use_db: bool) -> None:
        """设置管理器是否使用数据库

        Args:
            use_db: 是否使用数据库
        """
        cls._use_db = use_db
        logger.info(f"{cls.__name__} 数据库使用状态设置为: {use_db}")
