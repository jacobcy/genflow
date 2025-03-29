"""内容类型管理器

负责管理内容类型的获取、保存等操作
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
from ..infra.base_manager import BaseManager


class ContentTypeManager(BaseManager):
    """内容类型管理器

    提供内容类型相关的操作，包括获取、保存等
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
        """初始化内容类型管理器"""
        if cls._initialized:
            return

        cls._load_content_types()
        cls._initialized = True
        logger.info("内容类型管理器初始化完成")

    @classmethod
    def _load_content_types(cls) -> None:
        """从常量加载内容类型"""
        for name, research_config in RESEARCH_CONFIG.items():
            writing_config = WRITING_CONFIG.get(name, {})

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

    @classmethod
    def get_content_type(cls, content_type_id: str) -> Optional[ContentTypeModel]:
        """获取指定ID的内容类型

        Args:
            content_type_id: 内容类型ID

        Returns:
            Optional[ContentTypeModel]: 内容类型对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._content_types.get(content_type_id)

    @classmethod
    def get_all_content_types(cls) -> Dict[str, ContentTypeModel]:
        """获取所有内容类型配置

        Returns:
            Dict[str, ContentTypeModel]: 内容类型字典，键为内容类型名称
        """
        cls.ensure_initialized()
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
            return None

        return cls.get_content_type(content_type_name)

    @classmethod
    def get_default_content_type(cls) -> ContentTypeModel:
        """获取默认内容类型（博客）

        Returns:
            ContentTypeModel: 默认内容类型
        """
        cls.ensure_initialized()
        content_type = cls.get_content_type(CONTENT_TYPE_BLOG)
        if content_type:
            return content_type

        # 如果BLOG类型不存在，创建一个默认的
        default_content_type = ContentTypeModel(
            name=CONTENT_TYPE_BLOG,
            depth=RESEARCH_DEPTH_MEDIUM,
            description="通用博客内容",
            word_count="1200-2000",
            focus="信息和观点",
            style="个性化、对话式",
            structure="引言-主体-结论",
            needs_expert=False,
            needs_data_analysis=False
        )

        # 保存到缓存
        cls._content_types[CONTENT_TYPE_BLOG] = default_content_type
        return default_content_type

    @classmethod
    def save_content_type(cls, content_type: ContentTypeModel) -> bool:
        """保存内容类型

        Args:
            content_type: 内容类型对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        # 保存到缓存
        cls._content_types[content_type.name] = content_type
        logger.info(f"内容类型保存成功: {content_type.name}")
        return True

    @classmethod
    def get_research_depth(cls, depth_name: str) -> str:
        """获取研究深度常量值

        Args:
            depth_name: 深度名称

        Returns:
            str: 研究深度常量值
        """
        depths = {
            "light": RESEARCH_DEPTH_LIGHT,
            "medium": RESEARCH_DEPTH_MEDIUM,
            "deep": RESEARCH_DEPTH_DEEP
        }
        return depths.get(depth_name.lower(), RESEARCH_DEPTH_MEDIUM)
