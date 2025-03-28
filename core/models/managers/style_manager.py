"""风格管理器模块

提供文章风格相关的管理功能，包括获取、创建和匹配文章风格。
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from ..content_manager_factory import BaseManager


class StyleManager(BaseManager):
    """风格管理器

    负责管理和操作文章风格，包括加载、查询、创建和保存风格。
    """

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 文章风格对象
        """
        cls.ensure_initialized()

        try:
            from ..article_style import get_style_by_name
            return get_style_by_name(style_name)
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"获取文章风格失败: {str(e)}")
            return None

    @classmethod
    def get_or_create_style(cls, text: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """通过文本获取或创建风格

        首先尝试将文本作为风格名称匹配，
        再尝试模糊匹配现有风格，如果仍然匹配不到，
        则将文本作为描述创建一个临时风格。

        Args:
            text: 风格名称或描述文本
            options: 其他选项和风格属性

        Returns:
            Optional[Any]: 风格对象
        """
        cls.ensure_initialized()

        try:
            from ..article_style import get_or_create_style
            return get_or_create_style(text, options)
        except Exception as e:
            logger.error(f"获取或创建风格失败: {str(e)}")
            return None

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[Any]:
        """根据风格类型查找匹配的风格

        Args:
            style_type: 风格类型

        Returns:
            Optional[Any]: 匹配的风格对象，如果找不到则返回None
        """
        cls.ensure_initialized()

        # 获取所有风格
        try:
            styles = cls.get_all_article_styles()

            # 精确匹配
            for style in styles.values():
                if hasattr(style, "type") and style.type == style_type:
                    return style

            # 模糊匹配
            for style in styles.values():
                if hasattr(style, "type") and style_type in style.type:
                    return style

            return None
        except Exception as e:
            logger.error(f"根据类型查找风格失败: {str(e)}")
            return None

    @classmethod
    def get_all_article_styles(cls) -> Dict[str, Any]:
        """获取所有文章风格配置

        Returns:
            Dict[str, Any]: 所有文章风格的字典，键为风格名称
        """
        cls.ensure_initialized()

        try:
            from ..article_style import load_article_styles
            return load_article_styles()
        except (ImportError, AttributeError) as e:
            logger.error(f"获取文章风格配置失败: {str(e)}")
            return {}

    @classmethod
    def get_platform_style(cls, platform: str) -> Optional[Any]:
        """根据平台名称获取对应的风格配置

        Args:
            platform: 平台名称

        Returns:
            Optional[Any]: 平台对应的风格对象
        """
        cls.ensure_initialized()

        try:
            from ..article_style import get_platform_style
            return get_platform_style(platform)
        except (ImportError, AttributeError) as e:
            logger.error(f"获取平台风格配置失败: {str(e)}")
            return None

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()

        try:
            from ..service.db_adapter import DBAdapter
            return DBAdapter.save_article_style(style)
        except Exception as e:
            logger.error(f"保存文章风格失败: {str(e)}")
            return False

    @classmethod
    def create_style_from_description(cls, description: str, options: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """根据文本描述创建风格对象

        Args:
            description: 风格的文本描述
            options: 其他选项和风格属性

        Returns:
            Optional[Any]: 创建的风格对象，如果失败则返回None
        """
        cls.ensure_initialized()

        try:
            from ..util import StyleFactory
            return StyleFactory.create_style_from_description(description, options)
        except Exception as e:
            logger.error(f"从描述创建风格对象失败: {str(e)}")
            return None

    @classmethod
    def is_compatible_with_content_type(cls, style: Any, content_type_name: str) -> bool:
        """检查风格是否与内容类型兼容

        Args:
            style: 风格对象
            content_type_name: 内容类型名称

        Returns:
            bool: 是否兼容
        """
        cls.ensure_initialized()

        try:
            if hasattr(style, "is_compatible_with_content_type"):
                return style.is_compatible_with_content_type(content_type_name)
            return True  # 默认兼容
        except Exception as e:
            logger.error(f"检查风格兼容性失败: {str(e)}")
            return False
