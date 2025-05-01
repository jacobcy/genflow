"""大纲适配器

负责大纲数据的临时存储操作。
"""

from typing import List, Optional, Any
from loguru import logger
from .outline_storage import OutlineStorage


class OutlineAdapter:
    """大纲适配器，负责处理大纲相关的临时存储操作"""

    @classmethod
    def initialize(cls) -> bool:
        """初始化大纲存储

        Returns:
            bool: 是否成功初始化
        """
        try:
            # 初始化大纲存储
            OutlineStorage.initialize()
            logger.info("大纲适配器初始化成功")
            return True
        except Exception as e:
            logger.error(f"大纲存储初始化失败: {str(e)}")
            return False

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 大纲对象或None
        """
        try:
            # 从临时存储获取大纲
            outline = OutlineStorage.get_outline(outline_id)
            if outline:
                logger.debug(f"已获取大纲: {outline_id}")
            else:
                logger.debug(f"大纲不存在: {outline_id}")
            return outline
        except Exception as e:
            logger.error(f"从临时存储获取大纲失败: {e}")
            return None

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> str:
        """保存大纲

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则自动生成

        Returns:
            str: 大纲ID
        """
        try:
            # 保存到临时存储
            result = OutlineStorage.save_outline(outline, outline_id)
            logger.info(f"已保存大纲: {result}")
            return result
        except Exception as e:
            logger.error(f"保存大纲到临时存储失败: {e}")
            # 确保返回字符串，避免None
            return outline_id if outline_id else ""

    @classmethod
    def update_outline(cls, outline_id: str, outline: Any) -> bool:
        """更新大纲

        Args:
            outline_id: 大纲ID
            outline: 新的大纲对象

        Returns:
            bool: 是否成功更新
        """
        try:
            # 更新临时存储中的大纲
            result = OutlineStorage.update_outline(outline_id, outline)
            if result:
                logger.info(f"已更新大纲: {outline_id}")
            else:
                logger.warning(f"更新大纲失败，可能不存在: {outline_id}")
            return result
        except Exception as e:
            logger.error(f"更新大纲失败: {e}")
            return False

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 从临时存储删除大纲
            result = OutlineStorage.delete_outline(outline_id)
            if result:
                logger.info(f"已删除大纲: {outline_id}")
            else:
                logger.warning(f"删除大纲失败，可能不存在: {outline_id}")
            return result
        except Exception as e:
            logger.error(f"从临时存储删除大纲失败: {e}")
            return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        try:
            # 从临时存储获取所有大纲ID
            outlines = OutlineStorage.list_outlines()
            logger.debug(f"获取到 {len(outlines)} 个大纲ID")
            return outlines
        except Exception as e:
            logger.error(f"获取大纲列表失败: {e}")
            return []
