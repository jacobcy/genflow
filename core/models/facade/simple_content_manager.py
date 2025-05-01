"""简单内容管理器

负责管理不带ID的临时内容对象，如basic_research、临时大纲等
仅作为门面，不参与具体逻辑
"""

from typing import Optional
from loguru import logger

from ..infra.base_manager import BaseManager
from ..research.basic_research import BasicResearch
from ..outline.basic_outline import BasicOutline


class SimpleContentManager(BaseManager):
    """简单内容管理器

    负责管理不带ID的临时内容对象，如basic_research、临时大纲等
    仅作为门面，不参与具体逻辑
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
        from ..research.research_adapter import ResearchAdapter
        from ..outline.outline_storage import OutlineStorage
        from ..outline.outline_adapter import OutlineAdapter

        # 初始化各模块
        ResearchAdapter.initialize()
        OutlineAdapter.initialize()

        cls._initialized = True
        logger.info("简单内容管理器初始化完成")

    #region 基础研究相关方法

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
    def save_basic_research(cls, research: BasicResearch, research_id: Optional[str] = None) -> str:
        """保存基础研究对象

        Args:
            research: 研究对象
            research_id: 可选的研究ID，如不提供则自动生成

        Returns:
            str: 研究ID
        """
        cls.ensure_initialized()
        from ..research.research_adapter import ResearchAdapter
        return ResearchAdapter.save_research(research, research_id)

    @classmethod
    def get_basic_research(cls, research_id: str) -> Optional[BasicResearch]:
        """获取基础研究对象

        Args:
            research_id: 研究ID

        Returns:
            Optional[BasicResearch]: 研究对象或None
        """
        cls.ensure_initialized()
        from ..research.research_adapter import ResearchAdapter
        return ResearchAdapter.get_research(research_id)

    @classmethod
    def update_basic_research(cls, research_id: str, research: BasicResearch) -> bool:
        """更新基础研究对象

        Args:
            research_id: 研究ID
            research: 研究对象

        Returns:
            bool: 是否成功更新
        """
        cls.ensure_initialized()
        from ..research.research_adapter import ResearchAdapter
        return ResearchAdapter.update_research(research_id, research)

    @classmethod
    def delete_basic_research(cls, research_id: str) -> bool:
        """删除基础研究对象

        Args:
            research_id: 研究ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..research.research_adapter import ResearchAdapter
        return ResearchAdapter.delete_research(research_id)

    #endregion

    #region 临时大纲相关方法

    @classmethod
    def create_basic_outline(cls, **kwargs) -> BasicOutline:
        """创建基础大纲对象

        Args:
            **kwargs: 大纲对象属性

        Returns:
            BasicOutline: 创建的大纲对象
        """
        cls.ensure_initialized()
        return BasicOutline(**kwargs)

    @classmethod
    def save_basic_outline(cls, outline: BasicOutline, outline_id: Optional[str] = None) -> str:
        """保存基础大纲对象

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            str: 大纲ID
        """
        cls.ensure_initialized()
        from ..outline.outline_adapter import OutlineAdapter
        return OutlineAdapter.save_outline(outline, outline_id)

    @classmethod
    def get_basic_outline(cls, outline_id: str) -> Optional[BasicOutline]:
        """获取基础大纲对象

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象或None
        """
        cls.ensure_initialized()
        from ..outline.outline_adapter import OutlineAdapter
        return OutlineAdapter.get_outline(outline_id)

    @classmethod
    def update_basic_outline(cls, outline_id: str, outline: BasicOutline) -> bool:
        """更新基础大纲对象

        Args:
            outline_id: 大纲ID
            outline: 大纲对象

        Returns:
            bool: 是否成功更新
        """
        cls.ensure_initialized()
        from ..outline.outline_adapter import OutlineAdapter
        return OutlineAdapter.update_outline(outline_id, outline)

    @classmethod
    def delete_basic_outline(cls, outline_id: str) -> bool:
        """删除基础大纲对象

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..outline.outline_adapter import OutlineAdapter
        return OutlineAdapter.delete_outline(outline_id)

    #endregion
