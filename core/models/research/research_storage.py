"""研究临时存储

提供研究的临时存储功能，用于存储生命周期短暂的研究对象，
例如草稿研究、临时研究等，这些对象不需要持久化到数据库。
"""

from typing import Dict, List, Optional, Any, Union
import uuid
from loguru import logger

from core.models.infra.temporary_storage import TemporaryStorage
from .basic_research import BasicResearch

class ResearchStorage:
    """研究临时存储类

    基于TemporaryStorage实现的研究专用临时存储。
    提供研究对象的临时存储和检索功能，支持过期时间和自动清理。
    """

    # 存储实例名称
    _STORAGE_NAME = "research_storage"
    
    # 默认过期时间（秒）
    _DEFAULT_TTL = 24 * 60 * 60  # 24小时
    
    # 存储实例
    _storage: Optional[TemporaryStorage] = None

    @classmethod
    def initialize(cls) -> None:
        """初始化研究临时存储"""
        if cls._storage is None:
            cls._storage = TemporaryStorage.get_instance(cls._STORAGE_NAME, cls._DEFAULT_TTL)
            logger.info("研究临时存储已初始化")

    @classmethod
    def get_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取临时研究

        Args:
            research_id: 研究ID

        Returns:
            Optional[BasicResearch]: 研究对象，不存在则返回None
        """
        cls.initialize()
        return cls._storage.get(research_id)

    @classmethod
    def save_research(cls, research: Union[BasicResearch, Dict[str, Any]], 
                     research_id: Optional[str] = None) -> str:
        """保存临时研究

        Args:
            research: 研究对象或字典
            research_id: 可选的研究ID，如不提供则自动生成

        Returns:
            str: 研究ID
        """
        cls.initialize()
        
        # 如果是字典，尝试转换为BasicResearch对象
        if isinstance(research, dict):
            try:
                research = BasicResearch.model_validate(research)
            except Exception as e:
                logger.warning(f"字典转换为研究对象失败: {e}")
                # 如果转换失败，直接存储字典
        
        # 如果没有提供ID，尝试从研究元数据中获取
        if research_id is None and hasattr(research, "metadata") and "research_id" in research.metadata:
            research_id = research.metadata["research_id"]
        
        # 保存研究
        return cls._storage.set(research_id, research)

    @classmethod
    def update_research(cls, research_id: str, 
                       research: Union[BasicResearch, Dict[str, Any]]) -> bool:
        """更新临时研究

        Args:
            research_id: 研究ID
            research: 新的研究对象或字典

        Returns:
            bool: 是否成功更新
        """
        cls.initialize()
        
        # 如果是字典，尝试转换为BasicResearch对象
        if isinstance(research, dict):
            try:
                research = BasicResearch.model_validate(research)
            except Exception as e:
                logger.warning(f"字典转换为研究对象失败: {e}")
                # 如果转换失败，直接存储字典
        
        return cls._storage.update(research_id, research)

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除临时研究

        Args:
            research_id: 研究ID

        Returns:
            bool: 是否成功删除
        """
        cls.initialize()
        return cls._storage.delete(research_id)

    @classmethod
    def list_researches(cls) -> List[str]:
        """获取所有临时研究ID列表

        Returns:
            List[str]: 研究ID列表
        """
        cls.initialize()
        return cls._storage.list_keys()