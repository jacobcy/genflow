"""配置管理器

负责管理各类配置对象，如style、content_type、platform等
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from ..infra.base_manager import BaseManager
# Import individual managers
from ..style.style_manager import StyleManager
from ..content_type.content_type_manager import ContentTypeManager
from ..platform.platform_manager import PlatformManager
# Import Pydantic models for type hinting
from ..style.article_style import ArticleStyle
from ..content_type.content_type import ContentTypeModel
from ..platform.platform import Platform


class ConfigManager(BaseManager):
    """配置管理器 (Facade)

    作为访问各类配置 (Style, ContentType, Platform) 的统一入口。
    本身不直接管理配置数据，而是代理到具体的 Manager。
    """

    _initialized = False

    @classmethod
    def initialize(cls, use_db: bool = True) -> None:
        """初始化配置管理器

        Args:
            use_db: 是否使用数据库，默认为True
        """
        if cls._initialized:
            return

        # Initialize individual managers
        logger.info("Initializing configuration managers...")
        StyleManager.initialize(use_db)
        ContentTypeManager.initialize() # ContentTypeManager doesn't use db flag currently
        PlatformManager.initialize()   # PlatformManager doesn't use db flag currently

        cls._initialized = True
        logger.info("ConfigManager facade initialization complete.")

    # --- Style Configuration Methods ---

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[ArticleStyle]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[ArticleStyle]: 风格对象或None
        """
        cls.ensure_initialized()
        # Delegate to StyleManager
        return StyleManager.get_article_style(style_name)

    @classmethod
    def get_default_style(cls) -> Optional[ArticleStyle]:
        """获取默认风格

        Returns:
            Optional[ArticleStyle]: 默认风格对象或None
        """
        cls.ensure_initialized()
        # Delegate to StyleManager
        return StyleManager.get_default_style()

    @classmethod
    def get_all_styles(cls) -> Dict[str, ArticleStyle]:
        """获取所有风格

        Returns:
            Dict[str, ArticleStyle]: 风格字典，键为风格名称，值为风格对象
        """
        cls.ensure_initialized()
        # Delegate to StyleManager
        return StyleManager.get_all_styles()

    # Note: create_style_from_description and find_style_by_type might be complex operations
    # that could potentially be moved to a higher-level service or factory later.
    # Keeping them here for now as direct delegations.

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[ArticleStyle]:
        """根据类型查找风格 (代理到 StyleManager)

        Args:
            style_type: 风格类型

        Returns:
            Optional[ArticleStyle]: 风格对象或None
        """
        cls.ensure_initialized()
        # Delegate to StyleManager
        return StyleManager.find_style_by_type(style_type)

    @classmethod
    def save_style(cls, style: ArticleStyle) -> bool:
        """保存风格 (代理到 StyleManager)

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        # Delegate to StyleManager
        return StyleManager.save_style(style)

    # --- Content Type Configuration Methods ---

    @classmethod
    def get_content_type(cls, name: str) -> Optional[ContentTypeModel]:
        """获取指定名称的内容类型配置

        Args:
            name: 内容类型名称 (e.g., "博客")

        Returns:
            Optional[ContentTypeModel]: 内容类型配置对象或None
        """
        cls.ensure_initialized()
        # Delegate to ContentTypeManager
        return ContentTypeManager.get_content_type(name)

    @classmethod
    def get_all_content_types(cls) -> Dict[str, ContentTypeModel]:
        """获取所有内容类型配置

        Returns:
            Dict[str, ContentTypeModel]: 内容类型配置字典
        """
        cls.ensure_initialized()
        # Delegate to ContentTypeManager
        return ContentTypeManager.get_all_content_types()

    @classmethod
    def get_default_content_type(cls) -> Optional[ContentTypeModel]:
        """获取默认的内容类型配置

        Returns:
            Optional[ContentTypeModel]: 默认内容类型配置对象或None
        """
        cls.ensure_initialized()
        # Delegate to ContentTypeManager
        return ContentTypeManager.get_default_content_type()

    @classmethod
    def get_content_type_by_category(cls, category: str) -> Optional[ContentTypeModel]:
        """根据类别获取内容类型配置 (代理到 ContentTypeManager)

        Args:
            category: 类别名称

        Returns:
            Optional[ContentTypeModel]: 内容类型配置对象或None
        """
        cls.ensure_initialized()
        # Delegate to ContentTypeManager
        return ContentTypeManager.get_content_type_by_category(category)


    # --- Platform Configuration Methods ---

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Platform]:
        """获取指定 ID 的平台配置

        Args:
            platform_id: 平台 ID (e.g., "zhihu")

        Returns:
            Optional[Platform]: 平台配置对象或None
        """
        cls.ensure_initialized()
        # Delegate to PlatformManager
        return PlatformManager.get_platform(platform_id)

    @classmethod
    def get_platform_by_name(cls, name: str) -> Optional[Platform]:
        """根据名称获取平台配置 (大小写不敏感)

        Args:
            name: 平台名称 (e.g., "知乎")

        Returns:
            Optional[Platform]: 平台配置对象或None
        """
        cls.ensure_initialized()
        # Delegate to PlatformManager
        return PlatformManager.get_platform_by_name(name)

    @classmethod
    def get_all_platforms(cls) -> Dict[str, Platform]:
        """获取所有平台配置

        Returns:
            Dict[str, Platform]: 平台配置字典
        """
        cls.ensure_initialized()
        # Delegate to PlatformManager
        return PlatformManager.get_all_platforms()
