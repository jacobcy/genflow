"""大纲管理模块

提供大纲的内存管理功能，包括基础的CRUD操作。
仅负责基础数据结构的管理，不涉及具体业务逻辑。
"""

from typing import Dict, List, Optional, Any, ClassVar
from datetime import datetime
from loguru import logger
from uuid import uuid4

from ..infra.base_manager import BaseManager
from core.models.outline.basic_outline import BasicOutline, OutlineNode


class OutlineManager(BaseManager):
    """大纲管理器

    提供大纲对象的基础管理功能，包括内存存储、获取、删除等。
    仅处理基础的数据存储需求，不包含业务逻辑。
    """

    _outlines: ClassVar[Dict[str, BasicOutline]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化大纲管理器"""
        if cls._initialized:
            return

        cls._initialized = True
        logger.info("大纲管理器初始化完成")

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[BasicOutline]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._outlines.get(outline_id)

    @classmethod
    def save_outline(cls, outline: BasicOutline) -> bool:
        """保存大纲

        Args:
            outline: 大纲对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 更新时间戳
        outline.updated_at = datetime.now()

        # 获取或生成大纲ID
        outline_id = None

        # 优先从metadata中获取ID
        if hasattr(outline, "metadata") and isinstance(outline.metadata, dict):
            outline_id = outline.metadata.get("outline_id")

        # 如果没有，生成新ID
        if not outline_id:
            outline_id = str(uuid4())
            # 保存到metadata
            outline.metadata["outline_id"] = outline_id

        # 保存到缓存
        cls._outlines[outline_id] = outline
        logger.info(f"大纲保存成功: {outline_id} ({outline.title})")
        return True

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        if outline_id in cls._outlines:
            del cls._outlines[outline_id]
            logger.info(f"大纲删除成功: {outline_id}")
            return True
        logger.warning(f"大纲不存在，无法删除: {outline_id}")
        return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        cls.ensure_initialized()
        return list(cls._outlines.keys())
