"""内容类型和文章风格管理器

该模块提供统一的接口来加载和管理内容类型和文章风格配置。
作为上层应用与具体配置之间的桥梁。

注意：此类现在作为向后兼容的外观(Facade)，内部委托给更具体的管理器。
"""

from typing import Dict, List, Optional, Any
from loguru import logger


class ContentManager:
    """内容类型和文章风格统一管理器

    该类是配置和文章管理的统一接口，作为外部访问的入口点。
    不包含具体业务逻辑，仅作为适配器将请求转发给相应的管理器。

    注意：现在本类主要是为了向后兼容，新代码应直接使用具体的管理器。
    """

    _is_initialized: bool = False
    _use_db: bool = True

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化管理器

        初始化所有服务组件，包括配置服务和文章服务

        Args:
            use_db: 是否使用数据库存储，默认为True
        """
        from .content_manager_factory import ContentManagerFactory

        cls._use_db = use_db
        ContentManagerFactory.initialize(use_db)

        # 标记初始化完成
        cls._is_initialized = True
        logger.info("ContentManager初始化完成")

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._is_initialized:
            cls.initialize()

    #----------------------------------#
    # 内容类型相关方法                  #
    #----------------------------------#

    @classmethod
    def get_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取指定ID的内容类型"""
        cls.ensure_initialized()

        from .content_manager_factory import get_content_type_manager
        content_type_manager = get_content_type_manager()
        if content_type_manager:
            return content_type_manager.get_content_type(content_type_id)
        return None

    @classmethod
    def get_all_content_types(cls) -> Dict[str, Any]:
        """获取所有内容类型配置"""
        cls.ensure_initialized()

        from .content_manager_factory import get_content_type_manager
        content_type_manager = get_content_type_manager()
        if content_type_manager:
            return content_type_manager.get_all_content_types()
        return {}

    @classmethod
    def get_content_type_by_category(cls, category: str) -> Optional[Any]:
        """根据类别名称获取内容类型"""
        cls.ensure_initialized()

        from .content_manager_factory import get_content_type_manager
        content_type_manager = get_content_type_manager()
        if content_type_manager:
            return content_type_manager.get_content_type_by_category(category)
        return None

    @classmethod
    def save_content_type(cls, content_type: Any) -> bool:
        """保存内容类型到数据库"""
        cls.ensure_initialized()

        from .content_manager_factory import get_content_type_manager
        content_type_manager = get_content_type_manager()
        if content_type_manager:
            return content_type_manager.save_content_type(content_type)
        return False

    #----------------------------------#
    # 文章风格相关方法                  #
    #----------------------------------#

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.get_article_style(style_name)
        return None

    @classmethod
    def get_or_create_style(cls, text: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """通过文本获取或创建风格"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.get_or_create_style(text, options)
        return None

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[Any]:
        """根据风格类型查找匹配的风格"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.find_style_by_type(style_type)
        return None

    @classmethod
    def get_all_article_styles(cls) -> Dict[str, Any]:
        """获取所有文章风格配置"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.get_all_article_styles()
        return {}

    @classmethod
    def get_platform_style(cls, platform: str) -> Optional[Any]:
        """根据平台名称获取对应的风格配置"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.get_platform_style(platform)
        return None

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.save_article_style(style)
        return False

    @classmethod
    def create_style_from_description(cls, description: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """根据文本描述创建风格对象"""
        cls.ensure_initialized()

        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            return style_manager.create_style_from_description(description, options)
        return None

    #----------------------------------#
    # 平台相关方法                     #
    #----------------------------------#

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Any]:
        """获取指定ID的平台配置"""
        cls.ensure_initialized()

        from .content_manager_factory import get_platform_manager
        platform_manager = get_platform_manager()
        if platform_manager:
            return platform_manager.get_platform(platform_id)
        return None

    @classmethod
    def get_all_platforms(cls) -> Dict[str, Any]:
        """获取所有平台配置"""
        cls.ensure_initialized()

        from .content_manager_factory import get_platform_manager
        platform_manager = get_platform_manager()
        if platform_manager:
            return platform_manager.get_all_platforms()
        return {}

    #----------------------------------#
    # 兼容性相关方法                    #
    #----------------------------------#

    @classmethod
    def is_compatible(cls, content_type_id: str, style_name: str) -> bool:
        """检查内容类型和风格是否兼容"""
        cls.ensure_initialized()

        # 获取内容类型和风格
        content_type = cls.get_content_type(content_type_id)
        if not content_type:
            return False

        style = cls.get_article_style(style_name)
        if not style:
            return False

        # 检查是否兼容
        from .content_manager_factory import get_style_manager
        style_manager = get_style_manager()
        if style_manager:
            content_type_name = getattr(content_type, "name", content_type_id)
            return style_manager.is_compatible_with_content_type(style, content_type_name)

        return True  # 默认兼容

    #----------------------------------#
    # 文章相关方法                      #
    #----------------------------------#

    @classmethod
    def get_article(cls, article_id: str) -> Optional[Any]:
        """获取指定ID的文章"""
        cls.ensure_initialized()

        from .content_manager_factory import get_article_manager
        article_manager = get_article_manager()
        if article_manager:
            return article_manager.get_article(article_id)
        return None

    @classmethod
    def save_article(cls, article: Any) -> bool:
        """保存文章到数据库"""
        cls.ensure_initialized()

        from .content_manager_factory import get_article_manager
        article_manager = get_article_manager()
        if article_manager:
            return article_manager.save_article(article)
        return False

    #----------------------------------#
    # 话题相关方法                      #
    #----------------------------------#

    @classmethod
    def get_topic(cls, topic_id: str) -> Optional[Any]:
        """获取指定ID的话题"""
        cls.ensure_initialized()

        from .content_manager_factory import get_topic_manager
        topic_manager = get_topic_manager()
        if topic_manager:
            return topic_manager.get_topic(topic_id)
        return None

    @classmethod
    def save_topic(cls, topic: Any) -> bool:
        """保存话题到数据库"""
        cls.ensure_initialized()

        from .content_manager_factory import get_topic_manager
        topic_manager = get_topic_manager()
        if topic_manager:
            return topic_manager.save_topic(topic)
        return False

    #----------------------------------#
    # 大纲相关方法                      #
    #----------------------------------#

    @classmethod
    def get_outline(cls, outline_id: str) -> Optional[Any]:
        """获取指定ID的文章大纲"""
        cls.ensure_initialized()

        from .content_manager_factory import get_outline_manager
        outline_service = get_outline_manager()
        if outline_service:
            return outline_service.get_outline(outline_id)
        return None

    @classmethod
    def save_outline(cls, outline: Any, outline_id: Optional[str] = None) -> Optional[str]:
        """保存文章大纲到临时存储"""
        cls.ensure_initialized()

        from .content_manager_factory import get_outline_manager
        outline_service = get_outline_manager()
        if outline_service:
            return outline_service.save_outline(outline, outline_id)
        return None

    @classmethod
    def delete_outline(cls, outline_id: str) -> bool:
        """删除文章大纲"""
        cls.ensure_initialized()

        from .content_manager_factory import get_outline_manager
        outline_service = get_outline_manager()
        if outline_service:
            return outline_service.delete_outline(outline_id)
        return False

    @classmethod
    def list_outlines(cls) -> List[str]:
        """列出所有大纲ID"""
        cls.ensure_initialized()

        from .content_manager_factory import get_outline_manager
        outline_service = get_outline_manager()
        if outline_service:
            return outline_service.list_outlines()
        return []
