"""大纲管理工具

提供大纲管理相关的功能，包括获取、保存、删除和列出大纲，
以及大纲的类型转换等。
"""

from typing import Dict, Any, Optional, List, Union, TYPE_CHECKING
from loguru import logger

# 避免循环导入
if TYPE_CHECKING:
    from ..article_outline import ArticleOutline

class OutlineManager:
    """大纲管理工具类

    提供大纲相关的管理功能，包括获取、保存、删除和列出大纲。
    同时提供大纲的类型转换功能。
    """

    @staticmethod
    def get_outline(outline_id: str) -> Optional['ArticleOutline']:
        """获取指定ID的文章大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[ArticleOutline]: 文章大纲对象，不存在则返回None
        """
        try:
            from ..article_outline import ArticleOutline
            from ..service.temporary_storage import OutlineStorage

            # 确保临时存储已初始化
            OutlineStorage.initialize()

            # 从临时存储获取大纲
            raw_outline = OutlineStorage.get_outline(outline_id)
            if not raw_outline:
                return None

            # 转换为ArticleOutline对象
            if isinstance(raw_outline, ArticleOutline):
                return raw_outline

            # 如果返回的是字典，创建ArticleOutline对象
            if isinstance(raw_outline, dict):
                return ArticleOutline(**raw_outline)

            # 如果有to_outline方法，调用它
            if hasattr(raw_outline, 'to_outline') and callable(getattr(raw_outline, 'to_outline')):
                return raw_outline.to_outline()

            logger.warning(f"无法将{type(raw_outline)}转换为ArticleOutline")
            return None
        except Exception as e:
            logger.error(f"获取大纲失败: {str(e)}")
            return None

    @staticmethod
    def save_outline(outline: Any, outline_id: Optional[str] = None) -> Optional[str]:
        """保存文章大纲到临时存储

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则使用对象ID或自动生成

        Returns:
            Optional[str]: 大纲ID，如保存失败则返回None
        """
        try:
            from ..service.temporary_storage import OutlineStorage

            # 确保临时存储已初始化
            OutlineStorage.initialize()

            # 保存到临时存储
            return OutlineStorage.save_outline(outline, outline_id)
        except Exception as e:
            logger.error(f"保存大纲失败: {str(e)}")
            return None

    @staticmethod
    def delete_outline(outline_id: str) -> bool:
        """删除文章大纲

        从临时存储中删除指定的大纲。

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        try:
            from ..service.temporary_storage import OutlineStorage

            # 确保临时存储已初始化
            OutlineStorage.initialize()

            # 删除大纲
            return OutlineStorage.delete_outline(outline_id)
        except Exception as e:
            logger.error(f"删除大纲失败: {str(e)}")
            return False

    @staticmethod
    def list_outlines() -> List[str]:
        """列出所有大纲ID

        获取当前存储在临时存储中的所有大纲ID。

        Returns:
            List[str]: 大纲ID列表
        """
        try:
            from ..service.temporary_storage import OutlineStorage

            # 确保临时存储已初始化
            OutlineStorage.initialize()

            # 列出所有大纲
            return OutlineStorage.list_outlines()
        except Exception as e:
            logger.error(f"列出大纲失败: {str(e)}")
            return []
