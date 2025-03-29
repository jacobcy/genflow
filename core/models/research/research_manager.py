"""研究报告管理模块

提供研究报告的内存管理功能，包括基础的CRUD操作。
仅负责基础数据结构的管理，不涉及具体业务逻辑。
"""

from typing import Dict, List, Optional, Any, ClassVar
from datetime import datetime
from loguru import logger
from uuid import uuid4

from ..infra.base_manager import BaseManager
from .basic_research import BasicResearch


class ResearchManager(BaseManager):
    """研究报告管理器

    提供研究报告对象的基础管理功能，包括内存存储、获取、删除等。
    仅处理基础的数据存储需求，不包含业务逻辑。
    """

    _researches: ClassVar[Dict[str, BasicResearch]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化研究报告管理器"""
        if cls._initialized:
            return

        cls._initialized = True
        logger.info("研究报告管理器初始化完成")

    @classmethod
    def get_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取指定ID的研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            Optional[BasicResearch]: 研究报告对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._researches.get(research_id)

    @classmethod
    def save_research(cls, research: BasicResearch) -> bool:
        """保存研究报告

        Args:
            research: 研究报告对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 更新时间戳
        if hasattr(research, "research_timestamp"):
            research.research_timestamp = datetime.now()

        # 获取或生成研究报告ID
        research_id = None

        # 优先从对象本身获取ID
        if hasattr(research, "id"):
            research_id = getattr(research, "id")
        # 其次从metadata中获取ID
        elif hasattr(research, "metadata") and isinstance(research.metadata, dict):
            research_id = research.metadata.get("research_id")

        # 如果没有，生成新ID
        if not research_id:
            research_id = str(uuid4())
            # 保存到metadata
            if hasattr(research, "metadata") and isinstance(research.metadata, dict):
                research.metadata["research_id"] = research_id

        # 保存到缓存
        cls._researches[research_id] = research
        logger.info(f"研究报告保存成功: {research_id} ({research.title})")
        return True

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        if research_id in cls._researches:
            del cls._researches[research_id]
            logger.info(f"研究报告删除成功: {research_id}")
            return True
        logger.warning(f"研究报告不存在，无法删除: {research_id}")
        return False

    @classmethod
    def list_researches(cls) -> List[str]:
        """获取所有研究报告ID列表

        Returns:
            List[str]: 研究报告ID列表
        """
        cls.ensure_initialized()
        return list(cls._researches.keys())
