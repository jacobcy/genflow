"""大纲管理模块

提供大纲的内存管理功能，包括基础的CRUD操作。
仅负责基础数据结构的管理，不涉及具体业务逻辑。
"""

from typing import Dict, List, Optional, Type, TypeVar, Generic, Any
from datetime import datetime
from loguru import logger
from uuid import uuid4

from core.models.infra.base_manager import BaseManager
from core.models.outline.basic_outline import BasicOutline, OutlineNode

class OutlineManager(BaseManager[BasicOutline]):
    """大纲管理器

    提供大纲对象的基础管理功能，包括内存存储、获取、删除等。
    仅处理基础的数据存储需求，不包含业务逻辑。
    """

    _initialized: bool = False
    _model_class = BasicOutline
    _id_field = "outline_id"  # 大纲ID存储在metadata中
    _timestamp_field = "updated_at"
    _metadata_field = "metadata"

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化大纲管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        cls._use_db = use_db
        cls._initialized = True
        logger.info("大纲管理器初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[BasicOutline]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象，不存在则返回None
        """
        # 使用基类的get_entity方法
        return cls.get_entity(outline_id)

    @classmethod
    def save_outline(cls, outline: BasicOutline) -> bool:
        """保存大纲

        Args:
            outline: 大纲对象

        Returns:
            bool: 是否成功保存
        """
        # 使用基类的save_entity方法
        return cls.save_entity(outline)

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        # 使用基类的delete_entity方法
        return cls.delete_entity(outline_id)

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        # 使用基类的list_entities方法
        return cls.list_entities()
