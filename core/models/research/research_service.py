"""研究报告服务模块

此模块提供研究报告相关的服务方法，用于创建、获取和管理研究报告对象。
作为接口层，统一提供研究报告操作的入口，不包含具体业务逻辑。
"""

from typing import Dict, List, Optional, Any
from loguru import logger
import uuid
from datetime import datetime

from .basic_research import BasicResearch, KeyFinding, Source, ExpertInsight
from .research import TopicResearch


class ResearchService:
    """研究报告服务类，提供研究报告操作的静态方法

    作为基础服务层，仅提供统一的接口包装，不包含业务逻辑。
    具体的存储实现由ResearchManager负责。
    """

    _instance = None
    _initialized = False

    @classmethod
    def _get_manager(cls):
        """获取研究报告管理器实例

        Returns:
            ResearchManager: 研究报告管理器实例
        """
        if not cls._instance:
            # 延迟导入，避免循环依赖
            from .research_manager import ResearchManager
            cls._instance = ResearchManager
            cls._initialized = True
        return cls._instance

    @classmethod
    def create_research(cls, title: str, content_type: str, **kwargs) -> BasicResearch:
        """创建新的研究报告

        Args:
            title: 研究标题
            content_type: 内容类型
            **kwargs: 其他研究报告属性

        Returns:
            BasicResearch: 创建的研究报告对象
        """
        research = BasicResearch(title=title, content_type=content_type, **kwargs)
        return research

    @classmethod
    def create_from_json(cls, data: Dict[str, Any]) -> BasicResearch:
        """从JSON数据创建研究报告

        Args:
            data: 研究报告的JSON数据

        Returns:
            BasicResearch: 创建的研究报告对象
        """
        return BasicResearch.model_validate(data)

    @classmethod
    def create_topic_research(cls, basic_research: BasicResearch, topic_id: str) -> TopicResearch:
        """创建话题研究报告

        Args:
            basic_research: 基础研究报告
            topic_id: 话题ID

        Returns:
            TopicResearch: 话题研究报告对象
        """
        return TopicResearch.from_basic_research(basic_research, topic_id)

    @classmethod
    def get_research(cls, research_id: str) -> Optional[BasicResearch]:
        """根据ID获取研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            Optional[BasicResearch]: 研究报告对象，如果不存在则返回None
        """
        manager = cls._get_manager()
        # 确保管理器初始化
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()
        return manager.get_research(research_id) if hasattr(manager, "get_research") else None

    @classmethod
    def save_research(cls, research: BasicResearch, research_id: Optional[str] = None) -> Optional[str]:
        """保存研究报告

        Args:
            research: 要保存的研究报告对象
            research_id: 可选的研究报告ID，如不提供则生成新ID

        Returns:
            Optional[str]: 保存成功返回研究报告ID，失败返回None
        """
        # 生成唯一ID用于保存
        storage_id = research_id

        # 如果是TopicResearch并且有id字段，优先使用
        if hasattr(research, "id"):
            storage_id = getattr(research, "id")
        # 否则使用参数传入的ID或生成新ID
        else:
            storage_id = research_id or str(uuid.uuid4())
            # 尝试将ID保存到元数据中
            if hasattr(research, "metadata") and isinstance(research.metadata, dict):
                research.metadata["research_id"] = storage_id

        # 调用管理器保存
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()

        success = False
        if hasattr(manager, "save_research"):
            success = manager.save_research(research)

        return storage_id if success else None

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除研究报告

        Args:
            research_id: 要删除的研究报告ID

        Returns:
            bool: 删除是否成功
        """
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()
        return manager.delete_research(research_id) if hasattr(manager, "delete_research") else False

    @classmethod
    def list_researches(cls) -> List[str]:
        """获取所有研究报告ID列表

        Returns:
            List[str]: 研究报告ID列表
        """
        manager = cls._get_manager()
        if hasattr(manager, "ensure_initialized"):
            manager.ensure_initialized()

        # 检查list_researches方法是否存在
        if hasattr(manager, "list_researches"):
            return manager.list_researches()

        # 如果方法不存在，返回空列表
        logger.warning("研究报告管理器中没有list_researches方法")
        return []

    @classmethod
    def create_key_finding(cls, content: str, importance: float = 0.5, sources: Optional[List[Dict[str, Any]]] = None) -> KeyFinding:
        """创建关键发现

        Args:
            content: 发现内容
            importance: 重要性评分(0-1)
            sources: 来源列表

        Returns:
            KeyFinding: 关键发现对象
        """
        sources_list = []
        if sources:
            for source_data in sources:
                source = Source(**source_data)
                sources_list.append(source)

        return KeyFinding(
            content=content,
            importance=importance,
            sources=sources_list
        )

    @classmethod
    def create_source(cls, name: str, url: Optional[str] = None, **kwargs) -> Source:
        """创建信息来源

        Args:
            name: 来源名称
            url: 来源URL
            **kwargs: 其他来源属性

        Returns:
            Source: 信息来源对象
        """
        return Source(name=name, url=url, **kwargs)

    @classmethod
    def create_expert_insight(cls, expert_name: str, content: str, **kwargs) -> ExpertInsight:
        """创建专家见解

        Args:
            expert_name: 专家姓名
            content: 见解内容
            **kwargs: 其他专家见解属性

        Returns:
            ExpertInsight: 专家见解对象
        """
        return ExpertInsight(expert_name=expert_name, content=content, **kwargs)

    @classmethod
    def from_simple_research(cls,
                            title: str,
                            content: str,
                            key_points: List[Dict[str, Any]],
                            references: List[Dict[str, Any]],
                            content_type: str) -> BasicResearch:
        """从简单版本的研究结果创建标准BasicResearch

        Args:
            title: 研究标题
            content: 研究内容
            key_points: 关键点列表
            references: 参考资料列表
            content_type: 内容类型

        Returns:
            BasicResearch: 基础研究结果对象
        """
        return BasicResearch.from_simple_research(
            title=title,
            content=content,
            key_points=key_points,
            references=references,
            content_type=content_type
        )
