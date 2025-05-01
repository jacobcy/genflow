"""大纲临时存储

提供大纲的临时存储功能，用于存储生命周期短暂的大纲对象，
例如草稿大纲、临时大纲等，这些对象不需要持久化到数据库。
"""

from typing import Dict, List, Optional, Any, Union
import uuid
from loguru import logger

from core.models.infra.temporary_storage import TemporaryStorage
from .basic_outline import BasicOutline

class OutlineStorage:
    """大纲临时存储类

    基于TemporaryStorage实现的大纲专用临时存储。
    提供大纲对象的临时存储和检索功能，支持过期时间和自动清理。
    """

    # 存储实例名称
    _STORAGE_NAME = "outline_storage"
    
    # 默认过期时间（秒）
    _DEFAULT_TTL = 24 * 60 * 60  # 24小时
    
    # 存储实例
    _storage: Optional[TemporaryStorage] = None

    @classmethod
    def initialize(cls) -> None:
        """初始化大纲临时存储"""
        if cls._storage is None:
            cls._storage = TemporaryStorage.get_instance(cls._STORAGE_NAME, cls._DEFAULT_TTL)
            logger.info("大纲临时存储已初始化")

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[BasicOutline]:
        """获取临时大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象，不存在则返回None
        """
        cls.initialize()
        return cls._storage.get(outline_id)

    @classmethod
    def save_outline(cls, outline: Union[BasicOutline, Dict[str, Any]], 
                    outline_id: Optional[str] = None) -> str:
        """保存临时大纲

        Args:
            outline: 大纲对象或字典
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            str: 大纲ID
        """
        cls.initialize()
        
        # 如果是字典，尝试转换为BasicOutline对象
        if isinstance(outline, dict):
            try:
                outline = BasicOutline.model_validate(outline)
            except Exception as e:
                logger.warning(f"字典转换为大纲对象失败: {e}")
                # 如果转换失败，直接存储字典
        
        # 如果没有提供ID，尝试从大纲元数据中获取
        if outline_id is None and hasattr(outline, "metadata") and "outline_id" in outline.metadata:
            outline_id = outline.metadata["outline_id"]
        
        # 保存大纲
        return cls._storage.set(outline_id, outline)

    @classmethod
    def update_outline(cls, outline_id: str, 
                      outline: Union[BasicOutline, Dict[str, Any]]) -> bool:
        """更新临时大纲

        Args:
            outline_id: 大纲ID
            outline: 新的大纲对象或字典

        Returns:
            bool: 是否成功更新
        """
        cls.initialize()
        
        # 如果是字典，尝试转换为BasicOutline对象
        if isinstance(outline, dict):
            try:
                outline = BasicOutline.model_validate(outline)
            except Exception as e:
                logger.warning(f"字典转换为大纲对象失败: {e}")
                # 如果转换失败，直接存储字典
        
        return cls._storage.update(outline_id, outline)

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除临时大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        cls.initialize()
        return cls._storage.delete(outline_id)

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有临时大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        cls.initialize()
        return cls._storage.list_keys()