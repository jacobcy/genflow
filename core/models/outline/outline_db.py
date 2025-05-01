"""大纲数据库模型

定义大纲的数据库模型，包括数据库表结构和序列化/反序列化方法。
与basic_outline.py中的模型对应，用于数据持久化。
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

from core.models.db.session import Base, get_db

class OutlineNode(Base):
    """大纲节点数据库模型"""
    __tablename__ = "outline_node"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    outline_id = Column(String(50), ForeignKey("outline.id"), nullable=False, index=True)
    parent_id = Column(String(50), nullable=True, index=True)

    title = Column(String(500), nullable=False)
    level = Column(Integer, nullable=False, default=1)
    content = Column(Text, nullable=True, default="")
    order = Column(Integer, nullable=False, default=0)

    # 元数据 - 不能使用metadata作为字段名，因为它是SQLAlchemy的保留字
    meta_data = Column(Text, nullable=True, default="{}")

    outline = relationship("Outline", back_populates="nodes")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 节点数据字典
        """
        try:
            metadata_str = str(self.meta_data) if self.meta_data is not None else "{}"
            metadata = json.loads(metadata_str)
        except:
            metadata = {}

        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "content": str(self.content) if self.content is not None else "",
            "metadata": metadata,
            "parent_id": self.parent_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], outline_id: str, parent_id: Optional[str] = None) -> "OutlineNode":
        """从字典创建模型实例

        Args:
            data: 节点数据字典
            outline_id: 所属大纲ID
            parent_id: 父节点ID

        Returns:
            OutlineNode: 节点模型实例
        """
        metadata = json.dumps(data.get("metadata", {}))

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            outline_id=outline_id,
            parent_id=parent_id,
            title=data.get("title", ""),
            level=data.get("level", 1),
            content=data.get("content", ""),
            meta_data=metadata
        )


class Outline(Base):
    """大纲数据库模型"""
    __tablename__ = "outline"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True, default="")

    # 分类与关联
    content_type = Column(String(50), nullable=False, default="article")
    source = Column(String(50), nullable=False, default="manual")
    topic_id = Column(String(50), nullable=True, index=True)
    article_id = Column(String(50), nullable=True, index=True)

    # 元数据 - 不能使用metadata作为字段名，因为它是SQLAlchemy的保留字
    meta_data = Column(Text, nullable=True, default="{}")
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 关系
    nodes = relationship("OutlineNode", back_populates="outline", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict: 大纲数据字典
        """
        try:
            metadata_str = str(self.meta_data) if self.meta_data is not None else "{}"
            metadata = json.loads(metadata_str)
        except:
            metadata = {}

        # 构建节点树
        nodes_dict = {}
        root_nodes = []

        # 先建立节点字典
        for node in self.nodes:
            node_metadata = {}
            try:
                if node.meta_data is not None:
                    node_metadata = json.loads(str(node.meta_data))
            except:
                pass

            nodes_dict[node.id] = {
                "id": node.id,
                "title": node.title,
                "level": node.level,
                "content": str(node.content) if node.content is not None else "",
                "children": [],
                "metadata": node_metadata
            }

        # 构建树结构
        for node in self.nodes:
            parent_id_str = str(node.parent_id) if node.parent_id is not None else None
            if parent_id_str is None:
                # 根节点
                root_nodes.append(nodes_dict[node.id])
            elif node.parent_id in nodes_dict:
                # 添加到父节点的children中
                nodes_dict[node.parent_id]["children"].append(nodes_dict[node.id])

        created_at_iso = None
        if self.created_at is not None:
            created_at_iso = self.created_at.isoformat()

        updated_at_iso = None
        if self.updated_at is not None:
            updated_at_iso = self.updated_at.isoformat()

        return {
            "id": self.id,
            "title": self.title,
            "description": str(self.description) if self.description is not None else "",
            "content_type": self.content_type,
            "source": self.source,
            "topic_id": self.topic_id,
            "article_id": self.article_id,
            "nodes": root_nodes,
            "metadata": metadata,
            "created_at": created_at_iso,
            "updated_at": updated_at_iso
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        """从字典创建模型实例

        Args:
            data: 大纲数据字典

        Returns:
            Outline: 大纲模型实例
        """
        # 序列化JSON字段
        metadata = json.dumps(data.get("metadata", {}))

        created_at = data.get("created_at", datetime.now())
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at)
            except:
                created_at = datetime.now()

        updated_at = data.get("updated_at", datetime.now())
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at)
            except:
                updated_at = datetime.now()

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            description=data.get("description", ""),
            content_type=data.get("content_type", "article"),
            source=data.get("source", "manual"),
            topic_id=data.get("topic_id"),
            article_id=data.get("article_id"),
            meta_data=metadata,
            created_at=created_at,
            updated_at=updated_at
        )

    def create_nodes_from_tree(self, nodes_data: List[Dict[str, Any]], parent_id: Optional[str] = None) -> List[OutlineNode]:
        """从嵌套树结构创建节点

        Args:
            nodes_data: 节点数据列表
            parent_id: 父节点ID

        Returns:
            List[OutlineNode]: 创建的节点列表
        """
        result = []

        for i, node_data in enumerate(nodes_data):
            # 创建节点
            node = OutlineNode(
                id=node_data.get("id", str(uuid.uuid4())),
                outline_id=str(self.id) if self.id is not None else "",
                parent_id=parent_id,
                title=node_data.get("title", ""),
                level=node_data.get("level", 1),
                content=node_data.get("content", ""),
                order=i,
                meta_data=json.dumps(node_data.get("metadata", {}))
            )
            result.append(node)

            # 递归创建子节点
            if "children" in node_data and node_data["children"]:
                # 将node.id转换为字符串，避免类型错误
                node_id_str = str(node.id) if node.id is not None else None
                child_nodes = self.create_nodes_from_tree(node_data["children"], node_id_str)
                result.extend(child_nodes)

        return result
