"""基础管理器

所有管理器类的基类，定义了通用接口和属性
"""

from typing import Dict, List, Optional, Any, Type, Generic, TypeVar, ClassVar, cast
from abc import ABC
from loguru import logger
from datetime import datetime
from uuid import uuid4

# 定义泛型类型变量
T = TypeVar('T')

class BaseManager(Generic[T], ABC):
    """基础管理器

    所有管理器类的抽象基类，定义了通用接口和属性

    由于这是一个抽象基类，所有子类需要实现其接口，或者使用默认实现

    泛型参数T表示管理器管理的实体类型
    """

    # 类变量
    _initialized: bool = False
    _use_db: bool = False
    _model_class: Optional[Type[Any]] = None
    _entities: Dict[str, Any] = {}
    _id_field: str = "id"
    _timestamp_field: str = "updated_at"
    _metadata_field: str = "metadata"

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化

        如果管理器未初始化，则调用initialize方法。
        此方法在每次调用管理器方法之前都应该被调用，以确保管理器处于初始化状态。
        """
        if not cls._initialized:
            cls.initialize(cls._use_db)

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化管理器

        执行管理器的初始化操作，如加载数据、连接数据库等。
        子类应该覆盖此方法以实现自己的初始化逻辑。

        Args:
            use_db: 是否使用数据库
        """
        cls._use_db = use_db
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

    @classmethod
    def get_entity(cls, entity_id: str) -> Optional[Any]:
        """获取指定ID的实体

        通用的实体获取方法，子类可以覆盖以实现特定的获取逻辑

        Args:
            entity_id: 实体ID

        Returns:
            Optional[Any]: 实体对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._entities.get(entity_id)

    @classmethod
    def save_entity(cls, entity: Any) -> bool:
        """保存实体

        通用的实体保存方法，子类可以覆盖以实现特定的保存逻辑

        Args:
            entity: 实体对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 更新时间戳
        if hasattr(entity, cls._timestamp_field):
            setattr(entity, cls._timestamp_field, datetime.now())

        # 获取或生成实体ID
        entity_id = None

        # 优先从实体本身获取ID
        if hasattr(entity, cls._id_field):
            entity_id = getattr(entity, cls._id_field)
        # 其次从metadata中获取ID
        elif hasattr(entity, cls._metadata_field) and isinstance(getattr(entity, cls._metadata_field), dict):
            entity_id = getattr(entity, cls._metadata_field).get(f"{cls._id_field}")

        # 如果没有，生成新ID
        if not entity_id:
            entity_id = str(uuid4())
            # 保存ID
            if hasattr(entity, cls._id_field):
                setattr(entity, cls._id_field, entity_id)
            elif hasattr(entity, cls._metadata_field) and isinstance(getattr(entity, cls._metadata_field), dict):
                getattr(entity, cls._metadata_field)[f"{cls._id_field}"] = entity_id

        # 保存到缓存
        cls._entities[entity_id] = entity
        logger.info(f"{cls.__name__}实体保存成功: {entity_id}")
        return True

    @classmethod
    def delete_entity(cls, entity_id: str) -> bool:
        """删除实体

        通用的实体删除方法，子类可以覆盖以实现特定的删除逻辑

        Args:
            entity_id: 实体ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        if entity_id in cls._entities:
            del cls._entities[entity_id]
            logger.info(f"{cls.__name__}实体删除成功: {entity_id}")
            return True
        logger.warning(f"{cls.__name__}实体不存在，无法删除: {entity_id}")
        return False

    @classmethod
    def list_entities(cls) -> List[str]:
        """获取所有实体ID列表

        通用的实体列表获取方法，子类可以覆盖以实现特定的列表获取逻辑

        Returns:
            List[str]: 实体ID列表
        """
        cls.ensure_initialized()
        return list(cls._entities.keys())
