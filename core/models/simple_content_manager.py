"""简单内容管理器

负责管理不带ID的临时内容对象，如basic_research等
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .infra.base_manager import BaseManager
from .research.basic_research import BasicResearch


class SimpleContentManager(BaseManager):
    """简单内容管理器

    负责管理不带ID的临时内容对象，如basic_research等
    """

    _initialized = False

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化简单内容管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        # 初始化研究管理等
        from .research.research_manager import ResearchManager
        ResearchManager.initialize()

        cls._initialized = True
        logger.info("简单内容管理器初始化完成")

    @classmethod
    def create_basic_research(cls, **kwargs) -> BasicResearch:
        """创建基础研究对象

        Args:
            **kwargs: 研究对象属性

        Returns:
            BasicResearch: 创建的研究对象
        """
        cls.ensure_initialized()
        return BasicResearch(**kwargs)

    @classmethod
    def save_basic_research(cls, research: BasicResearch) -> bool:
        """保存基础研究对象

        Args:
            research: 研究对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from .research.research_manager import ResearchManager
        return ResearchManager.save_research(research)

    @classmethod
    def get_basic_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取基础研究对象

        Args:
            research_id: 研究ID

        Returns:
            Optional[BasicResearch]: 研究对象或None
        """
        cls.ensure_initialized()
        from .research.research_manager import ResearchManager
        return ResearchManager.get_research(research_id)
