"""研究报告数据库模型

提供研究报告的数据库模型定义，包括ORM映射和转换方法。
"""

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
import json
from datetime import datetime
import uuid
from typing import Dict, Any

from core.models.db.session import Base
from .basic_research import BasicResearch, Source, KeyFinding, ExpertInsight


class Research(Base):
    """研究报告数据库模型"""
    __tablename__ = "research"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content_type = Column(String(50), nullable=False)
    background = Column(Text, nullable=True)
    data_analysis = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    report = Column(Text, nullable=True)

    # 分类与关联
    topic_id = Column(String(50), nullable=True, index=True)

    # 元数据 - 不能使用metadata作为字段名，因为它是SQLAlchemy的保留字
    meta_data = Column(Text, nullable=True, default="{}")
    research_timestamp = Column(DateTime, nullable=False, default=datetime.now)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # 关系
    insights = relationship("ResearchInsight", back_populates="research", cascade="all, delete-orphan")
    findings = relationship("ResearchFinding", back_populates="research", cascade="all, delete-orphan")
    sources = relationship("ResearchSource", back_populates="research", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示

        Returns:
            Dict[str, Any]: 字典形式的研究报告
        """
        # 处理JSON字段
        try:
            metadata_str = str(getattr(self, "meta_data", "{}"))
            metadata = json.loads(metadata_str)
        except:
            metadata = {}

        # 安全地获取时间戳
        def get_iso_time(dt_attr):
            dt = getattr(self, dt_attr, None)
            if dt and hasattr(dt, "isoformat"):
                return dt.isoformat()
            return None

        research_timestamp_iso = get_iso_time("research_timestamp")
        created_at_iso = get_iso_time("created_at")
        updated_at_iso = get_iso_time("updated_at")

        # 转换关联对象
        expert_insights = [insight.to_dict() for insight in self.insights]
        key_findings = [finding.to_dict() for finding in self.findings]
        sources = [source.to_dict() for source in self.sources]

        return {
            "id": self.id,
            "title": self.title,
            "content_type": self.content_type,
            "background": self.background,
            "data_analysis": self.data_analysis,
            "summary": self.summary,
            "report": self.report,
            "topic_id": self.topic_id,
            "expert_insights": expert_insights,
            "key_findings": key_findings,
            "sources": sources,
            "metadata": metadata,
            "research_timestamp": research_timestamp_iso,
            "created_at": created_at_iso,
            "updated_at": updated_at_iso
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Research":
        """从字典创建模型实例

        Args:
            data: 研究报告数据字典

        Returns:
            Research: 研究报告模型实例
        """
        # 序列化JSON字段
        meta_data = json.dumps(data.get("metadata", {}))

        # 处理日期字段
        research_timestamp = data.get("research_timestamp", datetime.now())
        if isinstance(research_timestamp, str):
            try:
                research_timestamp = datetime.fromisoformat(research_timestamp)
            except:
                research_timestamp = datetime.now()

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

        # 创建主记录
        research = cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content_type=data.get("content_type", ""),
            background=data.get("background"),
            data_analysis=data.get("data_analysis"),
            summary=data.get("summary"),
            report=data.get("report"),
            topic_id=data.get("topic_id"),
            meta_data=meta_data,
            research_timestamp=research_timestamp,
            created_at=created_at,
            updated_at=updated_at
        )

        return research

    def to_basic_research(self) -> BasicResearch:
        """转换为BasicResearch对象

        将数据库模型转换为应用层模型对象

        Returns:
            BasicResearch: 基础研究报告对象
        """
        # 确保从ORM加载的属性是Python原生类型，而不是SQLAlchemy的描述符
        # 这段代码假设在实际使用时数据已经从数据库加载，属性是真实值
        def safe_get(attr_name, default=None):
            try:
                value = getattr(self, attr_name, default)
                # 对于从ORM加载的实例，属性已经是Python原生类型
                return value if value is not None else default
            except:
                return default

        # 处理JSON字段
        try:
            metadata_str = safe_get("meta_data", "{}")
            if not isinstance(metadata_str, str):
                metadata_str = str(metadata_str) if metadata_str else "{}"
            metadata = json.loads(metadata_str)
        except:
            metadata = {}

        # 转换关联对象
        expert_insights = [insight.to_model() for insight in self.insights]
        key_findings = [finding.to_model() for finding in self.findings]
        sources = [source.to_model() for source in self.sources]

        # 安全地获取属性
        title = safe_get("title", "")
        content_type = safe_get("content_type", "")
        background = safe_get("background")
        data_analysis = safe_get("data_analysis")
        summary = safe_get("summary")
        report = safe_get("report")
        research_timestamp = safe_get("research_timestamp", datetime.now())

        return BasicResearch(
            title=title,
            content_type=content_type,
            background=background,
            data_analysis=data_analysis,
            summary=summary,
            report=report,
            expert_insights=expert_insights,
            key_findings=key_findings,
            sources=sources,
            metadata=metadata,
            research_timestamp=research_timestamp
        )


class ResearchSource(Base):
    """研究报告来源数据库模型"""
    __tablename__ = "research_source"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    research_id = Column(String(50), ForeignKey("research.id"), nullable=False)
    name = Column(String(200), nullable=False)
    url = Column(String(500), nullable=True)
    author = Column(String(200), nullable=True)
    publish_date = Column(String(50), nullable=True)
    reliability_score = Column(Float, nullable=False, default=0.0)
    content_snippet = Column(Text, nullable=True)

    # 关系
    research = relationship("Research", back_populates="sources")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "author": self.author,
            "publish_date": self.publish_date,
            "reliability_score": self.reliability_score,
            "content_snippet": self.content_snippet
        }

    def to_model(self) -> Source:
        """转换为Source模型对象"""
        # 安全获取属性值
        def safe_get(attr_name, default=None):
            try:
                value = getattr(self, attr_name, default)
                return value if value is not None else default
            except:
                return default

        return Source(
            name=safe_get("name", ""),
            url=safe_get("url"),
            author=safe_get("author"),
            publish_date=safe_get("publish_date"),
            reliability_score=float(safe_get("reliability_score", 0.0)),
            content_snippet=safe_get("content_snippet")
        )


class ResearchFinding(Base):
    """研究报告发现数据库模型"""
    __tablename__ = "research_finding"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    research_id = Column(String(50), ForeignKey("research.id"), nullable=False)
    content = Column(Text, nullable=False)
    importance = Column(Float, nullable=False, default=0.0)

    # 关系
    research = relationship("Research", back_populates="findings")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "content": self.content,
            "importance": self.importance
        }

    def to_model(self) -> KeyFinding:
        """转换为KeyFinding模型对象"""
        # 安全获取属性值
        def safe_get(attr_name, default=None):
            try:
                value = getattr(self, attr_name, default)
                return value if value is not None else default
            except:
                return default

        return KeyFinding(
            content=safe_get("content", ""),
            importance=float(safe_get("importance", 0.0)),
            sources=[]  # 在实际实现中应查询关联的sources
        )


class ResearchInsight(Base):
    """研究报告专家见解数据库模型"""
    __tablename__ = "research_insight"
    __table_args__ = {'extend_existing': True}

    id = Column(String(50), primary_key=True, index=True)
    research_id = Column(String(50), ForeignKey("research.id"), nullable=False)
    expert_name = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    field = Column(String(200), nullable=True)
    credentials = Column(Text, nullable=True)

    # 关系
    research = relationship("Research", back_populates="insights")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            "id": self.id,
            "expert_name": self.expert_name,
            "content": self.content,
            "field": self.field,
            "credentials": self.credentials
        }

    def to_model(self) -> ExpertInsight:
        """转换为ExpertInsight模型对象"""
        # 安全获取属性值
        def safe_get(attr_name, default=None):
            try:
                value = getattr(self, attr_name, default)
                return value if value is not None else default
            except:
                return default

        return ExpertInsight(
            expert_name=safe_get("expert_name", ""),
            content=safe_get("content", ""),
            field=safe_get("field"),
            credentials=safe_get("credentials")
        )
