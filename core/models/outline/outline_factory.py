"""大纲工厂模块

提供大纲的创建、转换和业务逻辑处理功能。
负责大纲对象的生命周期管理，但不涉及持久化操作。
"""

from typing import Dict, List, Optional, Any, Union
import uuid
from datetime import datetime
from loguru import logger

from .basic_outline import BasicOutline, OutlineNode

class OutlineFactory:
    """大纲工厂类，提供大纲的创建和业务操作

    负责大纲对象的创建、验证、转换等操作，
    但不直接处理存储逻辑。
    """

    @classmethod
    def create_outline(cls, title: str, content_type: str = "article",
                       sections: Optional[List[Dict]] = None, **kwargs) -> BasicOutline:
        """创建新的大纲

        Args:
            title: 大纲标题
            content_type: 内容类型，默认为文章
            sections: 初始章节列表，可选
            **kwargs: 其他大纲属性

        Returns:
            BasicOutline: 创建的大纲对象
        """
        # 确保sections是列表
        if sections is None:
            sections = []

        # 创建初始节点列表
        outline_nodes = []
        for i, section in enumerate(sections):
            node = OutlineNode(
                id=section.get("id", str(uuid.uuid4())),
                title=section.get("title", f"章节 {i+1}"),
                content=section.get("content", ""),
                level=section.get("level", 1),
                children=section.get("children", []),
                metadata=section.get("metadata", {})
            )
            outline_nodes.append(node)

        # 创建大纲对象
        outline_id = str(uuid.uuid4())
        now = datetime.now()
        outline = BasicOutline(
            title=title,
            nodes=outline_nodes,
            content_type=content_type,
            created_at=now,
            updated_at=now,
            metadata={
                "outline_id": outline_id,
                "created_at": now.isoformat()
            },
            **kwargs
        )

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
        """获取大纲

        通过ID从管理器获取大纲对象

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[BasicOutline]: 大纲对象，不存在则返回None
        """
        from .outline_manager import OutlineManager
        OutlineManager.ensure_initialized()
        return OutlineManager.get_outline(outline_id)

    @classmethod
    def save_outline(cls, outline: BasicOutline, outline_id: Optional[str] = None) -> Optional[str]:
        """保存大纲

        将大纲对象保存到管理器

        Args:
            outline: 大纲对象
            outline_id: 可选的大纲ID，如不提供则使用对象ID

        Returns:
            Optional[str]: 保存成功返回大纲ID，失败返回None
        """
        from .outline_manager import OutlineManager

        # 如果提供了ID，保存到元数据
        if outline_id and hasattr(outline, "metadata"):
            outline.metadata["outline_id"] = outline_id

        OutlineManager.ensure_initialized()
        success = OutlineManager.save_outline(outline)

        if success:
            # 返回元数据中保存的ID
            if hasattr(outline, "metadata") and "outline_id" in outline.metadata:
                return outline.metadata["outline_id"]
            # 退化方案，生成新ID
            return str(uuid.uuid4())
        return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        从管理器中删除指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        from .outline_manager import OutlineManager
        OutlineManager.ensure_initialized()
        return OutlineManager.delete_outline(outline_id)

    @classmethod
    def list_outlines(cls) -> List[str]:
        """获取所有大纲ID列表

        Returns:
            List[str]: 大纲ID列表
        """
        from .outline_manager import OutlineManager
        OutlineManager.ensure_initialized()
        return OutlineManager.list_outlines()

    @classmethod
    def to_article(cls, outline: Union[BasicOutline, Dict[str, Any]]) -> Any:
        """将大纲转换为文章对象

        使用转换器将大纲转换为文章对象

        Args:
            outline: 大纲对象或字典

        Returns:
            Any: 文章对象
        """
        from .outline_converter import OutlineConverter
        return OutlineConverter.to_basic_article(outline)

    @classmethod
    def to_text(cls, outline: Union[BasicOutline, Dict[str, Any]]) -> str:
        """将大纲转换为文本

        使用转换器将大纲转换为文本格式

        Args:
            outline: 大纲对象或字典

        Returns:
            str: 格式化文本
        """
        from .outline_converter import OutlineConverter
        return OutlineConverter.to_full_text(outline)

    @classmethod
    def validate_outline(cls, outline: BasicOutline) -> bool:
        """验证大纲有效性

        检查大纲对象是否有效

        Args:
            outline: 大纲对象

        Returns:
            bool: 是否有效
        """
        # 检查必要字段
        if not outline.title:
            logger.warning("大纲缺少标题")
            return False

        if not hasattr(outline, "nodes") or not outline.nodes:
            logger.warning("大纲缺少节点")
            return False

        return True
