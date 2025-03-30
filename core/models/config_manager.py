"""配置管理器

负责管理各类配置对象，如style、content_type等
"""

from typing import Dict, List, Optional, Any
from loguru import logger

from .infra.base_manager import BaseManager


class ConfigManager(BaseManager):
    """配置管理器

    负责管理各类配置对象，如style、content_type等
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

        # 初始化风格管理等
        from .style.style_manager import StyleManager
        StyleManager.initialize(use_db)

        cls._initialized = True
        logger.info("配置管理器初始化完成")

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 风格对象或None
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.get_article_style(style_name)

    @classmethod
    def get_default_style(cls) -> Any:
        """获取默认风格

        Returns:
            Any: 默认风格对象
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.get_default_style()

    @classmethod
    def get_all_styles(cls) -> Dict[str, Any]:
        """获取所有风格

        Returns:
            Dict[str, Any]: 风格字典，键为风格名称，值为风格对象
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.get_all_styles()

    @classmethod
    def create_style_from_description(cls, description: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """从描述创建风格

        Args:
            description: 风格描述
            options: 风格选项

        Returns:
            Any: 创建的风格对象
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.create_style_from_description(description, options)

    @classmethod
    def find_style_by_type(cls, style_type: str) -> Optional[Any]:
        """根据类型查找风格

        Args:
            style_type: 风格类型

        Returns:
            Optional[Any]: 风格对象或None
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.find_style_by_type(style_type)

    @classmethod
    def save_style(cls, style: Any) -> bool:
        """保存风格

        Args:
            style: 风格对象

        Returns:
            bool: 是否成功保存
        """
        cls.ensure_initialized()
        from .style.style_manager import StyleManager
        return StyleManager.save_style(style)
