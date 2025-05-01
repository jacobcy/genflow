"""内容类型管理器

负责管理内容类型的加载和访问，数据来源于 constants.py
"""

from typing import Dict, List, Optional, Any, ClassVar
from loguru import logger

from core.models.content_type.constants import (
    CONTENT_TYPE_FLASH_NEWS, CONTENT_TYPE_SOCIAL_MEDIA, CONTENT_TYPE_NEWS,
    CONTENT_TYPE_BLOG, CONTENT_TYPE_TUTORIAL, CONTENT_TYPE_REVIEW,
    CONTENT_TYPE_STORY, CONTENT_TYPE_PAPER, CONTENT_TYPE_RESEARCH_REPORT,
    CONTENT_TYPE_ANALYSIS, CONTENT_TYPE_TECH, CONTENT_TYPE_QA,
    CONTENT_TYPE_ENTERTAINMENT, CONTENT_TYPE_LIFE, CONTENT_TYPE_SCIENCE,
    RESEARCH_CONFIG, WRITING_CONFIG,
    RESEARCH_DEPTH_LIGHT, RESEARCH_DEPTH_MEDIUM, RESEARCH_DEPTH_DEEP,
    CATEGORY_TO_CONTENT_TYPE
)
from core.models.content_type.content_type import ContentTypeModel


class ContentTypeManager:
    """内容类型管理器

    从 constants.py 加载内容类型配置并提供访问接口。
    这是一个只读的配置管理器。
    """

    _content_types: ClassVar[Dict[str, ContentTypeModel]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化内容类型管理器，从常量加载数据"""
        if cls._initialized:
            return

        cls._load_content_types()
        cls._initialized = True
        logger.info("内容类型管理器初始化完成")

    @classmethod
    def _load_content_types(cls) -> None:
        """从常量加载内容类型到内存缓存"""
        cls._content_types = {} # Clear previous cache if re-initializing
        for name, research_config in RESEARCH_CONFIG.items():
            # Use default empty dict if writing config missing for a type
            writing_config = WRITING_CONFIG.get(name, {})
            # Use default values from constants if specific keys missing
            content_type = ContentTypeModel(
                name=name,
                depth=research_config.get("depth", RESEARCH_DEPTH_MEDIUM),
                description=research_config.get("description", ""),
                word_count=writing_config.get("word_count", "1000-2000"),
                focus=research_config.get("focus", ""),
                style=writing_config.get("style", ""),
                structure=writing_config.get("structure", ""),
                needs_expert=research_config.get("needs_expert", False),
                needs_data_analysis=research_config.get("needs_data_analysis", False)
            )
            cls._content_types[name] = content_type
        logger.debug(f"加载了 {len(cls._content_types)} 种内容类型配置")

    @classmethod
    def get_content_type(cls, content_type_name: str) -> Optional[ContentTypeModel]:
        """获取指定名称的内容类型配置

        Args:
            content_type_name: 内容类型名称 (e.g., "博客")

        Returns:
            Optional[ContentTypeModel]: 内容类型对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._content_types.get(content_type_name)

    @classmethod
    def get_all_content_types(cls) -> Dict[str, ContentTypeModel]:
        """获取所有内容类型配置

        Returns:
            Dict[str, ContentTypeModel]: 内容类型字典，键为内容类型名称
        """
        cls.ensure_initialized()
        # Return a copy to prevent external modification of the cache
        return cls._content_types.copy()

    @classmethod
    def get_content_type_by_category(cls, category: str) -> Optional[ContentTypeModel]:
        """根据类别名称获取内容类型

        Args:
            category: 类别名称

        Returns:
            Optional[ContentTypeModel]: 内容类型对象，不存在则返回None
        """
        cls.ensure_initialized()
        content_type_name = CATEGORY_TO_CONTENT_TYPE.get(category)
        if not content_type_name:
            logger.warning(f"类别 '{category}' 未找到对应的内容类型")
            return None

        return cls.get_content_type(content_type_name)

    @classmethod
    def get_default_content_type(cls) -> Optional[ContentTypeModel]:
        """获取默认内容类型（来自常量定义，例如博客）

        Returns:
            Optional[ContentTypeModel]: 默认内容类型，如果常量中未定义则返回None
        """
        cls.ensure_initialized()
        # Default type is defined by constant CONTENT_TYPE_BLOG
        return cls.get_content_type(CONTENT_TYPE_BLOG)
