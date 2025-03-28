"""大纲服务模块

提供文章大纲相关的高级服务功能，包括获取、保存和删除大纲。
与工具层的OutlineManager配合，提供更高层次的抽象。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from ..content_manager_factory import BaseManager


class OutlineFactory(BaseManager):
    """大纲服务

    负责提供大纲相关的高级服务功能，包括获取、保存、删除和转换大纲。
    注意：此类与工具层的util.outline_manager.OutlineManager协作，
    此类提供管理层API，而工具层类负责具体实现。
    """

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的文章大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 文章大纲对象，不存在则返回None
        """
        cls.ensure_initialized()

        try:
            from .outline_manager import OutlineManager
            return OutlineManager.get_outline(outline_id)
        except Exception as e:
            logger.error(f"获取大纲失败: {str(e)}")
            return None

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> Optional[str]:
        """保存文章大纲到临时存储

        注意：大纲是临时对象，不会持久化到数据库，只保存在内存中，
        程序重启后数据会丢失。

        Args:
            outline: 文章大纲对象
            outline_id: 可选的大纲ID，如不提供则使用对象ID或自动生成

        Returns:
            Optional[str]: 大纲ID，如保存失败则返回None
        """
        cls.ensure_initialized()

        try:
            from .outline_manager import OutlineManager
            return OutlineManager.save_outline(outline, outline_id)
        except Exception as e:
            logger.error(f"保存大纲失败: {str(e)}")
            return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除文章大纲

        从临时存储中删除指定的大纲。

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()

        try:
            from .outline_manager import OutlineManager
            return OutlineManager.delete_outline(outline_id)
        except Exception as e:
            logger.error(f"删除大纲失败: {str(e)}")
            return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """列出所有大纲ID

        获取当前存储在临时存储中的所有大纲ID。

        Returns:
            List[str]: 大纲ID列表
        """
        cls.ensure_initialized()

        try:
            from .outline_manager import OutlineManager
            return OutlineManager.list_outlines()
        except Exception as e:
            logger.error(f"列出大纲失败: {str(e)}")
            return []

    @classmethod
    def convert_outline_to_article(cls, outline: Any) -> Optional[Any]:
        """将大纲转换为文章

        Args:
            outline: 大纲对象

        Returns:
            Optional[Any]: 文章对象，转换失败则返回None
        """
        cls.ensure_initialized()

        try:
            from ..util.outline_converter import OutlineConverter
            return OutlineConverter.to_basic_article(outline)
        except Exception as e:
            logger.error(f"大纲转换为文章失败: {str(e)}")
            return None
