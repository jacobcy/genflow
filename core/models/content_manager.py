"""模型管理服务

简化的模型访问层，提供对系统各种模型的统一访问接口。
职责是协调不同类型的模型管理器，不包含业务逻辑。
"""

from typing import Dict, List, Optional, Any, Type
from loguru import logger

# 导入基础组件
from .style.style_manager import StyleManager
from .article.article_manager import ArticleManager
from .topic.topic_manager import TopicManager
from .research.research_manager import ResearchManager


class ContentManager:
    """内容管理服务

    提供对系统各类模型的统一访问接口，包括:
    - 简单内容类（不含ID的临时对象）：basic_research, basic_outline, basic_article
    - 持久内容类（含ID）：topic, research, article_outline, article
    - 配置类：content_type, platform, style, category
    - 过程类：progress, feedback

    对外提供统一的接口，内部按照职责将这四类内容分开管理。
    """

    # 初始化状态跟踪
    _simple_content_initialized = False
    _persistent_content_initialized = False
    _config_initialized = False
    _operation_initialized = False
    _use_db = True

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化内容管理服务

        Args:
            use_db: 是否使用数据库，默认为True
        """
        cls._use_db = use_db

        # 初始化四个主要组件
        cls._initialize_simple_content()
        cls._initialize_persistent_content()
        cls._initialize_config()
        cls._initialize_operation()

        logger.info("内容管理服务初始化完成")

    #----------------------------------#
    # 初始化方法                       #
    #----------------------------------#

    @classmethod
    def _initialize_simple_content(cls) -> None:
        """初始化简单内容管理组件"""
        if cls._simple_content_initialized:
            return

        # 初始化简单内容相关模块
        ResearchManager.initialize()

        cls._simple_content_initialized = True
        logger.debug("简单内容管理组件初始化完成")

    @classmethod
    def _initialize_persistent_content(cls) -> None:
        """初始化持久内容管理组件"""
        if cls._persistent_content_initialized:
            return

        # 初始化话题、文章等持久内容模块
        TopicManager.initialize()
        ArticleManager.initialize(cls._use_db)

        cls._persistent_content_initialized = True
        logger.debug("持久内容管理组件初始化完成")

    @classmethod
    def _initialize_config(cls) -> None:
        """初始化配置管理组件"""
        if cls._config_initialized:
            return

        # 初始化风格、平台等配置模块
        StyleManager.initialize(cls._use_db)

        cls._config_initialized = True
        logger.debug("配置管理组件初始化完成")

    @classmethod
    def _initialize_operation(cls) -> None:
        """初始化操作管理组件"""
        if cls._operation_initialized:
            return

        # 初始化进度、反馈等操作模块
        # 这里将来可以添加进度和反馈相关管理器的初始化

        cls._operation_initialized = True
        logger.debug("操作管理组件初始化完成")

    #----------------------------------#
    # 简单内容相关方法                 #
    #----------------------------------#

    @classmethod
    def create_basic_research(cls, **kwargs) -> Any:
        """创建基础研究对象

        Args:
            **kwargs: 研究对象属性

        Returns:
            Any: 创建的研究对象
        """
        cls._initialize_simple_content()
        from .research.basic_research import BasicResearch
        return BasicResearch(**kwargs)

    @classmethod
    def save_basic_research(cls, research: Any) -> bool:
        """保存基础研究对象

        Args:
            research: 研究对象

        Returns:
            bool: 是否成功保存
        """
        cls._initialize_simple_content()
        return ResearchManager.save_research(research)

    @classmethod
    def get_basic_research(cls, research_id: str) -> Optional[Any]:
        """获取基础研究对象

        Args:
            research_id: 研究ID

        Returns:
            Optional[Any]: 研究对象或None
        """
        cls._initialize_simple_content()
        return ResearchManager.get_research(research_id)

    #----------------------------------#
    # 持久内容相关方法                 #
    #----------------------------------#

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Any]:
        """获取指定ID的话题

        Args:
            topic_id: 话题ID

        Returns:
            Optional[Any]: 话题对象或None
        """
        cls._initialize_persistent_content()
        return TopicManager.get_topic(topic_id)

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题

        Args:
            topic: 话题对象

        Returns:
            bool: 是否成功保存
        """
        cls._initialize_persistent_content()
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
        cls._initialize_persistent_content()
        return TopicManager.create_topic(title, keywords, content_type)

    @classmethod
    def delete_topic(cls, topic_id: str) -> bool:
        """删除话题

        Args:
            topic_id: 话题ID

        Returns:
            bool: 是否成功删除
        """
        cls._initialize_persistent_content()
        return TopicManager.delete_topic(topic_id)

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Any]:
        """获取指定ID的文章

        Args:
            article_id: 文章ID

        Returns:
            Optional[Any]: 文章对象或None
        """
        cls._initialize_persistent_content()
        return ArticleManager.get_article(article_id)

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章

        Args:
            article: 文章对象

        Returns:
            bool: 是否成功保存
        """
        cls._initialize_persistent_content()
        return ArticleManager.save_article(article)

    @classmethod
    def get_articles_by_status(cls, status: str) -> List[Any]:
        """获取指定状态的文章

        Args:
            status: 文章状态

        Returns:
            List[Any]: 文章列表
        """
        cls._initialize_persistent_content()
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
        cls._initialize_persistent_content()
        return ArticleManager.update_article_status(article_id, status)

    #----------------------------------#
    # 配置相关方法                     #
    #----------------------------------#

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 风格对象或None
        """
        cls._initialize_config()
        return StyleManager.get_article_style(style_name)

    @classmethod
    def get_default_style(cls) -> Any:
        """获取默认风格

        Returns:
            Any: 默认风格对象
        """
        cls._initialize_config()
        return StyleManager.get_default_style()

    @classmethod
    def get_all_styles(cls) -> Dict[str, Any]:
        """获取所有风格

        Returns:
            Dict[str, Any]: 风格字典，键为风格名称
        """
        cls._initialize_config()
        return StyleManager.get_all_styles()

    @classmethod
    def create_style_from_description(cls, description: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """从描述创建风格

        Args:
            description: 风格描述文本
            options: 可选配置参数

        Returns:
            Any: 创建的风格对象
        """
        cls._initialize_config()
        return StyleManager.create_style_from_description(description, options)

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[Any]:
        """根据类型查找风格

        Args:
            style_type: 风格类型

        Returns:
            Optional[Any]: 匹配的风格对象或None
        """
        cls._initialize_config()
        return StyleManager.find_style_by_type(style_type)

    @classmethod
    def save_style(cls, style: Any) -> bool:
        """保存风格

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        cls._initialize_config()
        return StyleManager.save_style(style)

    #----------------------------------#
    # 操作和过程相关方法               #
    #----------------------------------#

    # 这里可以添加操作和过程相关方法
    # 例如创建进度、更新反馈等


# 向后兼容性别名
ModelService = ContentManager
