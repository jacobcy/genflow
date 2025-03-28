"""配置服务模块

处理内容类型、风格和平台配置的业务逻辑。
负责配置数据的加载、验证和管理。
"""

from typing import Dict, Optional, Any, List
from loguru import logger

class ConfigService:
    """配置服务类，处理内容类型、风格和平台配置的业务逻辑"""

    @classmethod
    def is_compatible(cls, content_type_id: str, style_id: str) -> bool:
        """检查内容类型和风格是否兼容

        Args:
            content_type_id: 内容类型ID
            style_id: 风格ID

        Returns:
            bool: 是否兼容
        """
        from ..content_manager import ContentManager
        return ContentManager.is_compatible(content_type_id, style_id)

    @classmethod
    def get_recommended_style_for_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取适合指定内容类型的推荐风格

        Args:
            content_type_id: 内容类型ID

        Returns:
            Optional[Any]: 推荐的风格配置
        """
        from ..content_manager import ContentManager
        return ContentManager.get_recommended_style_for_content_type(content_type_id)

    @classmethod
    def get_platform_style(cls, platform: str) -> Optional[Any]:
        """根据平台名称获取对应的风格配置

        Args:
            platform: 平台名称

        Returns:
            Optional[Any]: 平台风格配置
        """
        from ..content_manager import ContentManager
        return ContentManager.get_platform_style(platform)

    @classmethod
    def reload_platform(cls, platform_id: str) -> Optional[Any]:
        """重新加载特定平台配置

        当平台配置文件发生变化时调用，重新加载特定平台配置

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Any]: 更新后的平台配置
        """
        from ..content_manager import ContentManager
        return ContentManager.reload_platform(platform_id)

    @classmethod
    def reload_all_platforms(cls) -> Dict[str, Any]:
        """重新加载所有平台配置

        当有新的平台配置添加时调用，重新扫描并加载所有平台配置

        Returns:
            Dict[str, Any]: 更新后的平台配置字典
        """
        from ..content_manager import ContentManager
        return ContentManager.reload_all_platforms()

    @classmethod
    def sync_configs_to_db(cls, full_sync: bool = False) -> bool:
        """同步所有配置到数据库

        Args:
            full_sync: 是否执行完整同步（包括删除不存在的配置）

        Returns:
            bool: 是否成功同步
        """
        from ..content_manager import ContentManager
        if full_sync:
            return ContentManager.sync_configs_to_db_full()
        else:
            return ContentManager.sync_configs_to_db()

    @classmethod
    def save_content_type(cls, content_type: Any) -> bool:
        """保存内容类型到数据库

        Args:
            content_type: 内容类型对象

        Returns:
            bool: 是否成功保存
        """
        from ..content_manager import ContentManager
        return ContentManager.save_content_type(content_type)

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库

        Args:
            style: 文章风格对象

        Returns:
            bool: 是否成功保存
        """
        from ..content_manager import ContentManager
        return ContentManager.save_article_style(style)

    @classmethod
    def save_platform(cls, platform: Any) -> bool:
        """保存平台配置到数据库

        Args:
            platform: 平台配置对象

        Returns:
            bool: 是否成功保存
        """
        from ..content_manager import ContentManager
        return ContentManager.save_platform(platform)

    @classmethod
    def get_content_type_by_category(cls, category: str) -> Optional[Any]:
        """根据类别名称获取内容类型

        Args:
            category: 类别名称

        Returns:
            Optional[Any]: 内容类型配置
        """
        from ..content_manager import ContentManager
        return ContentManager.get_content_type_by_category(category)
