"""持久内容管理器

负责管理带ID的持久化内容对象，如topic、article等
"""

from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime

from ..infra.base_manager import BaseManager


class ContentManager(BaseManager):
    """持久内容管理器

    负责管理带ID的持久化内容对象，如topic、article等
    作为统一入口，委托具体操作给各专门的Manager类
    """

    _initialized = False

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化持久内容管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        # 初始化话题管理、文章管理等
        from ..topic.topic_manager import TopicManager
        from ..article.article_manager import ArticleManager
        from ..research.research_manager import ResearchManager
        from ..outline.outline_manager import OutlineManager

        TopicManager.initialize()
        ArticleManager.initialize(use_db)
        ResearchManager.initialize()
        OutlineManager.initialize()

        cls._initialized = True
        logger.info("持久内容管理器初始化完成")

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Any]:
        """获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Any]: 话题对象或None
        """
        cls.ensure_initialized()
        from ..topic.topic_manager import TopicManager
        return TopicManager.get_topic(topic_id)

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题

        Args:
            topic: 话题对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from ..topic.topic_manager import TopicManager
        return TopicManager.save_topic(topic)

    @classmethod
    def create_topic(cls, title: str, keywords: Optional[List[str]] = None,
                    content_type: Optional[str] = None) -> Optional[Any]:
        """创建新话题

        Args:
            title: 话题标题
            keywords: 话题关键词列表
            content_type: 内容类型ID

        Returns:
            Optional[Any]: 创建的话题对象，失败返回None
        """
        cls.ensure_initialized()
        from ..topic.topic_manager import TopicManager
        return TopicManager.create_topic(title, keywords, content_type)

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..topic.topic_manager import TopicManager
        return TopicManager.delete_topic(topic_id)

    @classmethod
    def get_research(cls, research_id: str) -> Optional[Any]:
        """获取指定ID的研究

        Args:
            research_id: 研究ID

        Returns:
            Optional[Any]: 研究对象或None
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory
        return ResearchFactory.get_research(research_id)

    @classmethod
    def save_research(cls, research: Any) -> bool:
        """保存研究

        Args:
            research: 研究对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory
        return ResearchFactory.save_research(research) is not None

    @classmethod
    def create_research(cls, topic_id: str, title: str,
                       content_type: Optional[str] = None, **kwargs) -> Optional[Any]:
        """创建新研究

        Args:
            topic_id: 关联的话题ID
            title: 研究标题
            content_type: 内容类型
            **kwargs: 其他研究属性

        Returns:
            Optional[Any]: 创建的研究对象，失败返回None
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory

        try:
            research = ResearchFactory.create_research(
                title=title,
                content_type=content_type or "general",
                topic_id=topic_id,
                **kwargs
            )
            research_id = ResearchFactory.save_research(research)
            if research_id:
                return research
            return None
        except Exception as e:
            logger.error(f"创建研究失败: {str(e)}")
            return None

    @classmethod
    def delete_research(cls, research_id: str) -> bool:
        """删除研究

        Args:
            research_id: 研究ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory
        return ResearchFactory.delete_research(research_id)

    @classmethod
    def validate_research(cls, research: Any) -> bool:
        """验证研究报告有效性

        Args:
            research: 研究报告对象

        Returns:
            bool: 是否有效
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory
        return ResearchFactory.validate_research(research)

    @classmethod
    def research_to_markdown(cls, research_id: str) -> str:
        """将研究报告转换为Markdown格式

        Args:
            research_id: 研究报告ID

        Returns:
            str: Markdown格式的文本，失败返回空字符串
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory

        research = ResearchFactory.get_research(research_id)
        if research:
            return ResearchFactory.to_markdown(research)
        return ""

    @classmethod
    def get_research_completeness(cls, research_id: str) -> Dict[str, Any]:
        """获取研究报告完整度评估

        Args:
            research_id: 研究报告ID

        Returns:
            Dict[str, Any]: 完整度评估结果，失败返回空字典
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory

        research = ResearchFactory.get_research(research_id)
        if research:
            return ResearchFactory.get_research_completeness(research)
        return {"overall": 0}

    @classmethod
    def create_simple_research(cls, topic_id: str, title: str, content: str,
                              key_points: Optional[List[Dict]] = None,
                              references: Optional[List[Dict]] = None,
                              content_type: str = "research") -> Optional[Any]:
        """从简化的研究数据创建研究报告

        Args:
            topic_id: 关联的话题ID
            title: 研究标题
            content: 研究内容
            key_points: 关键点列表
            references: 参考资料列表
            content_type: 内容类型

        Returns:
            Optional[Any]: 创建的研究对象，失败返回None
        """
        cls.ensure_initialized()
        from ..research.research_factory import ResearchFactory

        try:
            research = ResearchFactory.from_simple_research(
                title=title,
                content=content,
                key_points=key_points,
                references=references,
                content_type=content_type,
                topic_id=topic_id
            )
            research_id = ResearchFactory.save_research(research)
            if research_id:
                return research
            return None
        except Exception as e:
            logger.error(f"创建简化研究失败: {str(e)}")
            return None

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Any]:
        """获取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Any]: 文章对象或None
        """
        cls.ensure_initialized()
        from ..article.article_manager import ArticleManager
        return ArticleManager.get_article(article_id)

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from ..article.article_manager import ArticleManager
        return ArticleManager.save_article(article)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Any]:
        """获取指定状态的文章列表

        Args:
            status: 文章状态

        Returns:
            List[Any]: 文章对象列表
        """
        cls.ensure_initialized()
        from ..article.article_manager import ArticleManager
        return ArticleManager.get_articles_by_status(status)

    @classmethod
    def update_article_status(cls, article_id: str, status: str) -> bool:
        """更新文章状态

        Args:
            article_id: 文章ID
            status: 新状态

        Returns:
            bool: 是否成功更新
        """
        cls.ensure_initialized()
        from ..article.article_manager import ArticleManager
        return ArticleManager.update_article_status(article_id, status)

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的大纲

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 大纲对象或None
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory
        return OutlineFactory.get_outline(outline_id)

    @classmethod
    def save_outline(cls, outline: Any) -> bool:
        """保存大纲

        Args:
            outline: 大纲对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory
        return OutlineFactory.save_outline(outline) is not None

    @classmethod
    def create_outline(cls, title: str, content_type: str = "article",
                     sections: Optional[List[Dict]] = None, **kwargs) -> Optional[Any]:
        """创建新大纲

        Args:
            title: 大纲标题
            content_type: 内容类型，默认为文章
            sections: 初始章节列表，可选
            **kwargs: 其他大纲属性

        Returns:
            Optional[Any]: 创建的大纲对象，失败返回None
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory

        try:
            outline = OutlineFactory.create_outline(title, content_type, sections, **kwargs)
            outline_id = OutlineFactory.save_outline(outline)
            if outline_id:
                return outline
            return None
        except Exception as e:
            logger.error(f"创建大纲失败: {str(e)}")
            return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除大纲

        Args:
            outline_id: 大纲ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory
        return OutlineFactory.delete_outline(outline_id)

    @classmethod
    def outline_to_article(cls, outline_id: str) -> Optional[Any]:
        """将大纲转换为文章对象

        Args:
            outline_id: 大纲ID

        Returns:
            Optional[Any]: 文章对象，失败返回None
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory

        outline = OutlineFactory.get_outline(outline_id)
        if outline:
            return OutlineFactory.to_article(outline)
        return None

    @classmethod
    def outline_to_text(cls, outline_id: str) -> str:
        """将大纲转换为文本

        Args:
            outline_id: 大纲ID

        Returns:
            str: 文本内容，失败返回空字符串
        """
        cls.ensure_initialized()
        from ..outline.outline_factory import OutlineFactory

        outline = OutlineFactory.get_outline(outline_id)
        if outline:
            return OutlineFactory.to_text(outline)
        return ""

    @classmethod
    def delete_article(cls, article_id: str) -> bool:
        """删除文章

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功删除
        """
        cls.ensure_initialized()
        from ..article.article_manager import ArticleManager
        return ArticleManager.delete_article(article_id)

    @classmethod
    def create_article(cls, topic_id: str, title: str, **kwargs) -> Optional[Any]:
        """创建新文章

        Args:
            topic_id: 话题ID
            title: 文章标题
            **kwargs: 其他文章属性

        Returns:
            Optional[Any]: 创建的文章对象，失败返回None
        """
        cls.ensure_initialized()
        from ..article.article_factory import ArticleFactory
        from ..article.article import Article
        from uuid import uuid4

        try:
            # 创建基本文章
            article_id = kwargs.get("id", f"article_{uuid4().hex[:8]}")
            article = Article(
                id=article_id,
                topic_id=topic_id,
                title=title,
                **kwargs
            )

            # 计算文章指标
            ArticleFactory.calculate_article_metrics(article)

            # 保存文章
            from ..article.article_manager import ArticleManager
            if ArticleManager.save_article(article):
                return article
            return None
        except Exception as e:
            logger.error(f"创建文章失败: {str(e)}")
            return None
