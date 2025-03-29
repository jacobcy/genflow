"""大纲工厂模块

此模块提供大纲管理的工厂类，用于管理大纲的临时存储和加载。
作为数据库适配器与大纲管理器之间的桥接层。
"""

from typing import Dict, List, Optional, Any
import uuid
from loguru import logger

# 类型消除循环导入
OutlineType = Any


class OutlineManager:
    """大纲管理器，提供大纲的临时存储和获取服务

    此类作为数据库适配器与实际大纲管理器之间的桥梁，
    转发对大纲的操作请求。
    """

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[OutlineType]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[OutlineType]: 大纲对象，不存在则返回None
        """
        try:
            # 导入真正的大纲管理器
            from core.models.outline.outline_manager import OutlineManager as RealOutlineManager

            # 转发请求
            RealOutlineManager.ensure_initialized()
            return RealOutlineManager.get_outline(outline_id)
        except Exception as e:
            logger.error(f"获取大纲失败: {str(e)}")
            return None

    @classmethod
    def save_outline(cls, outline: OutlineType, outline_id: Optional[str] = None) -> Optional[str]:
        """保存大纲

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则使用对象ID

        Returns:
            Optional[str]: 保存成功返回大纲ID，失败返回None
        """
        try:
            # 导入真正的大纲管理器
            from core.models.outline.outline_manager import OutlineManager as RealOutlineManager

            # 如果提供了ID，保存到元数据
            if outline_id and hasattr(outline, "metadata"):
                outline.metadata["outline_id"] = outline_id

            # 转发请求
            RealOutlineManager.ensure_initialized()
            success = RealOutlineManager.save_outline(outline)

            if success:
                # 返回元数据中保存的ID
                if hasattr(outline, "metadata") and "outline_id" in outline.metadata:
                    return outline.metadata["outline_id"]
                # 退化方案，生成新ID
                return str(uuid.uuid4())
            return None
        except Exception as e:
            logger.error(f"保存大纲失败: {str(e)}")
            return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        try:
            # 导入真正的大纲管理器
            from core.models.outline.outline_manager import OutlineManager as RealOutlineManager

            # 转发请求
            RealOutlineManager.ensure_initialized()
            return RealOutlineManager.delete_outline(outline_id)
        except Exception as e:
            logger.error(f"删除大纲失败: {str(e)}")
            return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        try:
            # 导入真正的大纲管理器
            from core.models.outline.outline_manager import OutlineManager as RealOutlineManager

            # 转发请求
            RealOutlineManager.ensure_initialized()

            # 确保list_outlines方法存在
            if hasattr(RealOutlineManager, "list_outlines"):
                return RealOutlineManager.list_outlines()
            else:
                logger.warning("真正的大纲管理器中没有list_outlines方法")
                return []
        except Exception as e:
            logger.error(f"列出大纲失败: {str(e)}")
            return []
