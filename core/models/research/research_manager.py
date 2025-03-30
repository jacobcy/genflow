"""研究报告管理模块

提供研究报告的内存管理功能，包括基础的CRUD操作。
仅负责基础数据结构的管理，不涉及具体业务逻辑。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from uuid import uuid4

from ..infra.base_manager import BaseManager
from .basic_research import BasicResearch


class ResearchManager(BaseManager[BasicResearch]):
    """研究报告管理器

    提供研究报告对象的基础管理功能，包括内存存储、获取、删除等。
    仅处理基础的数据存储需求，不包含业务逻辑。
    """

    _initialized: bool = False
    _model_class = BasicResearch
    _id_field = "research_id"  # 注意BasicResearch没有id字段，使用metadata中的research_id
    _timestamp_field = "research_timestamp"
    _metadata_field = "metadata"

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化研究报告管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        cls._use_db = use_db
        cls._initialized = True
        logger.info("研究报告管理器初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def get_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取指定ID的研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            Optional[BasicResearch]: 研究报告对象，不存在则返回None
        """
        # 使用基类的get_entity方法
        return cls.get_entity(research_id)

    @classmethod
    def save_research(cls, research: BasicResearch) -> bool:
        """保存研究报告

        Args:
            research: 研究报告对象

        Returns:
            bool: 是否成功保存
        """
        # 使用基类的save_entity方法
        return cls.save_entity(research)

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            bool: 是否成功删除
        """
        # 使用基类的delete_entity方法
        return cls.delete_entity(research_id)

    @classmethod
    def list_researches(cls) -> List[str]:
        """获取所有研究报告ID列表

        Returns:
            List[str]: 研究报告ID列表
        """
        # 使用基类的list_entities方法
        return cls.list_entities()
