"""研究报告工厂模块

提供研究报告的创建、转换和业务逻辑处理功能。
负责研究对象的生命周期管理，但不涉及持久化操作。
"""

from typing import Dict, List, Optional, Any, Union, cast
import uuid
import logging
from datetime import datetime
from loguru import logger

from .basic_research import BasicResearch, KeyFinding, Source, ExpertInsight
from .research import TopicResearch
from .research_manager import ResearchManager
from .utils import validate_research_data, format_research_as_json

logger = logging.getLogger(__name__)

class ResearchFactory:
    """
    Research工厂类，提供研究报告相关的业务逻辑和操作方法。
    负责研究报告的创建、验证、转换和处理。
    """

    @classmethod
    def create_research(cls, title: str, content_type: str, topic_id: Optional[str] = None,
                       background: str = "", expert_insights: Optional[List[ExpertInsight]] = None,
                       key_findings: Optional[List[KeyFinding]] = None, sources: Optional[List[Source]] = None,
                       **kwargs) -> TopicResearch:
        """
        创建一个新的研究报告实例

        Args:
            title: 研究报告标题
            content_type: 内容类型，如'tech_analysis', 'market_research'等
            topic_id: 关联的话题ID
            background: 研究背景
            expert_insights: 专家见解列表
            key_findings: 关键发现列表
            sources: 信息来源列表
            **kwargs: 其他可选参数

        Returns:
            创建的TopicResearch实例
        """
        # 确保列表字段不为None
        expert_insights = expert_insights or []
        key_findings = key_findings or []
        sources = sources or []

        # 生成唯一ID
        research_id = kwargs.get("id") or f"research_{uuid.uuid4().hex[:8]}"

        # 创建研究报告实例
        research = TopicResearch(
            id=research_id,
            topic_id=topic_id or "",  # 确保topic_id不为None
            title=title,
            content_type=content_type,
            background=background,
            expert_insights=expert_insights,
            key_findings=key_findings,
            sources=sources,
            **kwargs
        )

        return research

    @classmethod
    def validate_research(cls, research: Union[BasicResearch, TopicResearch, Dict[str, Any]]) -> bool:
        """
        验证研究报告数据的完整性和有效性

        Args:
            research: 待验证的研究报告，可以是BasicResearch、TopicResearch或字典

        Returns:
            验证结果，True表示有效，False表示无效
        """
        # 使用utils中的验证工具
        is_valid, _ = validate_research_data(research)
        return is_valid

    @classmethod
    def get_research(cls, research_id: str) -> Optional[TopicResearch]:
        """
        根据ID获取研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            TopicResearch实例或None（如果未找到）
        """
        ResearchManager.ensure_initialized()
        result = ResearchManager.get_research(research_id)
        if result is not None and not isinstance(result, TopicResearch):
            # 如果结果不是TopicResearch类型，转换为TopicResearch
            return cast(TopicResearch, result)
        return result

    @classmethod
    def save_research(cls, research: Union[BasicResearch, TopicResearch, Dict[str, Any]]) -> str:
        """
        保存研究报告

        Args:
            research: 待保存的研究报告

        Returns:
            保存的研究报告ID
        """
        ResearchManager.ensure_initialized()

        # 如果是BasicResearch，转换为TopicResearch
        if isinstance(research, BasicResearch) and not isinstance(research, TopicResearch):
            research = TopicResearch.from_basic_research(research, topic_id="")  # 使用空字符串而非None

        # 如果是字典，转换为TopicResearch
        if isinstance(research, dict):
            research = TopicResearch(**research)

        # 验证数据
        if not cls.validate_research(research):
            raise ValueError("研究报告数据无效，无法保存")

        # 保存研究报告
        if ResearchManager.save_research(research):
            return research.id
        else:
            raise RuntimeError(f"保存研究报告失败: {research.id}")

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """
        删除研究报告

        Args:
            research_id: 研究报告ID

        Returns:
            是否成功删除
        """
        ResearchManager.ensure_initialized()
        return ResearchManager.delete_research(research_id)

    @classmethod
    def list_researches(cls) -> List[str]:
        """
        列出所有研究报告ID

        Returns:
            研究报告ID列表
        """
        ResearchManager.ensure_initialized()
        return ResearchManager.list_researches()

    @classmethod
    def create_key_finding(cls, content: str, importance: float = 0.5,
                          sources: Optional[List[Dict[str, Any]]] = None) -> KeyFinding:
        """
        创建关键发现

        Args:
            content: 关键发现内容
            importance: 重要性(0-1)
            sources: 相关来源数据

        Returns:
            KeyFinding实例
        """
        sources_data = sources or []
        # 转换字典为Source对象
        source_objects = []
        for source_dict in sources_data:
            if isinstance(source_dict, dict):
                source_objects.append(Source(**source_dict))
            else:
                source_objects.append(source_dict)

        return KeyFinding(content=content, importance=importance, sources=source_objects)

    @classmethod
    def create_source(cls, name: str, url: str = "", author: str = "",
                     reliability_score: float = 0.5, date: Optional[str] = None) -> Source:
        """
        创建信息来源

        Args:
            name: 来源名称
            url: 来源URL
            author: 作者
            reliability_score: 可靠性评分(0-1)
            date: 发布日期

        Returns:
            Source实例
        """
        # 如果未提供日期，使用当前日期
        current_date = datetime.now().strftime("%Y-%m-%d")
        source_date = date if date is not None else current_date

        return Source(
            name=name,
            url=url,
            author=author,
            reliability_score=reliability_score,
            publish_date=source_date  # 使用正确的参数名publish_date
        )

    @classmethod
    def create_expert_insight(cls, expert_name: str, content: str,
                            field: str = "", credentials: str = "") -> ExpertInsight:
        """
        创建专家见解

        Args:
            expert_name: 专家姓名
            content: 见解内容
            field: 专业领域
            credentials: 专家资质

        Returns:
            ExpertInsight实例
        """
        return ExpertInsight(
            expert_name=expert_name,
            content=content,
            field=field,
            credentials=credentials
        )

    @classmethod
    def from_simple_research(cls, title: str, content: str,
                            key_points: Optional[List[Dict[str, Any]]] = None,
                            references: Optional[List[Dict[str, Any]]] = None,
                            content_type: str = "research",
                            topic_id: Optional[str] = None) -> TopicResearch:
        """
        从简化的研究数据创建研究报告

        Args:
            title: 研究标题
            content: 研究内容
            key_points: 关键点列表，格式为[{"content": "...", "importance": 0.8}, ...]
            references: 参考资料列表，格式为[{"title": "...", "url": "..."}, ...]
            content_type: 内容类型
            topic_id: 话题ID

        Returns:
            TopicResearch实例
        """
        # 初始化列表
        key_points = key_points or []
        references = references or []

        # 创建背景信息（使用content作为背景）
        background = content

        # 转换关键点为KeyFinding
        key_findings = []
        for point in key_points:
            finding = cls.create_key_finding(
                content=point.get("content", ""),
                importance=point.get("importance", 0.5)
            )
            key_findings.append(finding)

        # 转换参考资料为Source
        sources = []
        for ref in references:
            source = cls.create_source(
                name=ref.get("title", ""),
                url=ref.get("url", ""),
                author=ref.get("author", ""),
                reliability_score=ref.get("reliability", 0.5),
                date=ref.get("date")
            )
            sources.append(source)

        # 创建研究报告
        research = cls.create_research(
            title=title,
            content_type=content_type,
            topic_id=topic_id,
            background=background,
            key_findings=key_findings,
            sources=sources
        )

        return research

    @classmethod
    def to_markdown(cls, research: Union[BasicResearch, TopicResearch, Dict[str, Any]]) -> str:
        """
        将研究报告转换为Markdown格式

        Args:
            research: 研究报告对象或字典

        Returns:
            str: Markdown格式的文本
        """
        from .utils import format_research_as_markdown
        return format_research_as_markdown(research)

    @classmethod
    def to_json(cls, research: Union[BasicResearch, TopicResearch]) -> Dict[str, Any]:
        """
        将研究报告转换为JSON格式

        Args:
            research: 研究报告对象

        Returns:
            Dict[str, Any]: 字典格式的研究报告
        """
        return format_research_as_json(research)

    @classmethod
    def get_research_completeness(cls, research: Union[BasicResearch, TopicResearch]) -> Dict[str, Any]:
        """
        获取研究报告完整度评估

        Args:
            research: 研究报告对象

        Returns:
            Dict[str, Any]: 完整度评估结果
        """
        from .utils import get_research_completeness
        return get_research_completeness(research)
