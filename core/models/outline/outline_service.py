"""大纲服务模块

此模块提供大纲相关的服务方法，用于创建、获取和管理大纲对象。
作为接口层，统一提供大纲操作的入口，不包含具体业务逻辑。
"""

from typing import Dict, List, Optional, Any
from loguru import logger
import uuid

from core.models.outline.basic_outline import BasicOutline, OutlineNode


class OutlineService:
    """大纲服务类，提供大纲操作的静态方法

    作为基础服务层，仅提供统一的接口包装，不包含业务逻辑。
    具体的存储实现由OutlineManager负责。
    """

    _instance = None
    _initialized = False

    @classmethod
    def _get_manager(cls):
        """获取大纲管理器实例

        Returns:
            OutlineManager: 大纲管理器实例
        """
        if not cls._instance:
            # 延迟导入，避免循环依赖
            from .outline_manager import OutlineManager
            cls._instance = OutlineManager
            cls._initialized = True
        return cls._instance

    @classmethod
    def create_outline(cls, title: str, content_type: str = "article", **kwargs) -> BasicOutline:
        """创建新的大纲

        Args:
            title: 大纲标题
            content_type: 内容类型
            **kwargs: 其他大纲属性

        Returns:
            BasicOutline: 创建的大纲对象
        """
        outline = BasicOutline(title=title, content_type=content_type, **kwargs)
        return outline

    @classmethod
    def create_from_json(cls, data: Dict[str, Any]) -> BasicOutline:
        """从JSON数据创建大纲

        Args:
            data: 大纲的JSON数据

        Returns:
            BasicOutline: 创建的大纲对象
        """
        return BasicOutline.model_validate(data)

    @classmethod
    def create_outline_node(cls, title: str, level: int = 1, content: str = "", **kwargs) -> OutlineNode:
        """创建大纲节点

        Args:
            title: 节点标题
            level: 节点级别
            content: 节点内容
            **kwargs: 其他节点属性

        Returns:
            OutlineNode: 创建的大纲节点
        """
        return OutlineNode(title=title, level=level, content=content, **kwargs)

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[BasicOutline]:
        """根据ID获取大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象，如果不存在则返回None
        """
        manager = cls._get_manager()
        # 确保管理器初始化
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()
        return manager.get_outline(outline_id) if hasattr(manager, "get_outline") else None

    @classmethod
    def save_outline(cls, outline: BasicOutline, outline_id: Optional[str] = None) -> Optional[str]:
        """保存大纲

        Args:
            outline: 要保存的大纲对象
            outline_id: 可选的大纲ID，如不提供则生成新ID

        Returns:
            Optional[str]: 保存成功返回大纲ID，失败返回None
        """
        # 生成唯一ID用于保存
        storage_id = outline_id or str(uuid.uuid4())

        # 将ID保存到元数据中
        outline.metadata["outline_id"] = storage_id

        # 调用管理器保存
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()

        success = False
        if hasattr(manager, "save_outline"):
            success = manager.save_outline(outline)

        return storage_id if success else None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 要删除的大纲ID

        Returns:
            bool: 删除是否成功
        """
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()
        return manager.delete_outline(outline_id) if hasattr(manager, "delete_outline") else False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()

        # 检查list_outlines方法是否存在
        if hasattr(manager, "list_outlines"):
            return manager.list_outlines()

        # 如果方法不存在，返回空列表
        logger.warning("大纲管理器中没有list_outlines方法")
        return []
