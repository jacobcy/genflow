"""配置适配器

负责内容类型、文章风格和平台配置的数据库访问。
"""

from typing import Dict, List, Optional, Any
from loguru import logger


class ConfigAdapter:
    """配置适配器，负责处理配置相关的数据库操作"""

    _is_initialized: bool = False

    @classmethod
    def initialize(cls) -> bool:
        """初始化数据库连接和表结构

        Returns:
            bool: 是否成功初始化
        """
        if cls._is_initialized:
            return True

        try:
            # 导入数据库初始化模块
            from core.models.db.initialize import initialize_all

            # 初始化数据库
            initialize_all()

            cls._is_initialized = True
            logger.info("配置适配器初始化成功")
            return True
        except ImportError as e:
            logger.warning(f"数据库模块导入失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            return False

    @classmethod
    def sync_config_to_db(cls, sync_mode: bool = True) -> bool:
        """同步配置文件到数据库

        将现有的配置文件数据同步到数据库中

        Args:
            sync_mode: 是否为同步模式。同步模式下会删除不在文件中的记录。

        Returns:
            bool: 是否成功同步
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入迁移工具
            from core.models.db.migrate_configs import migrate_all

            # 执行迁移，在sync_mode下执行完整同步（包括删除不存在的配置）
            migrate_all(sync_mode=sync_mode)

            logger.info(f"配置文件已成功同步到数据库 (sync_mode={sync_mode})")
            return True
        except Exception as e:
            logger.error(f"同步配置文件到数据库失败: {str(e)}")
            return False

    #
    # 内容类型相关方法
    #

    @classmethod
    def load_content_types(cls) -> Dict[str, Any]:
        """从数据库加载所有内容类型

        Returns:
            Dict[str, Any]: 内容类型字典
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.models.db.repository import content_type_repo

            # 获取所有内容类型
            content_types = content_type_repo.get_all()
            return {ct.id: ct for ct in content_types}
        except Exception as e:
            logger.error(f"从数据库加载内容类型失败: {str(e)}")
            return {}

    @classmethod
    def get_content_type(cls, content_type_id: str) -> Optional[Any]:
        """获取指定ID的内容类型

        Args:
            content_type_id: 内容类型ID

        Returns:
            Optional[Any]: 内容类型对象
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.models.db.repository import content_type_repo

            # 获取内容类型
            return content_type_repo.get(content_type_id)
        except Exception as e:
            logger.error(f"获取内容类型失败: {str(e)}")
            return None

    @classmethod
    def save_content_type(cls, content_type: Any) -> bool:
        """保存内容类型到数据库

        Args:
            content_type: 内容类型对象

        Returns:
            bool: 是否成功保存
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.models.db.repository import content_type_repo

            # 转换为字典
            content_type_dict = cls._get_content_type_dict(content_type)

            # 检查是否已存在
            existing = content_type_repo.get(content_type.id)
            if existing:
                # 更新
                content_type_repo.update(content_type.id, content_type_dict)
                logger.info(f"已更新内容类型: {content_type.id}")
            else:
                # 创建
                content_type_repo.create(content_type_dict)
                logger.info(f"已创建内容类型: {content_type.id}")

            return True
        except Exception as e:
            logger.error(f"保存内容类型失败: {str(e)}")
            return False

    @staticmethod
    def _get_content_type_dict(content_type: Any) -> Dict[str, Any]:
        """将内容类型对象转换为字典

        Args:
            content_type: 内容类型对象

        Returns:
            Dict[str, Any]: 内容类型字典
        """
        if hasattr(content_type, "to_dict"):
            return content_type.to_dict()

        return {
            "id": content_type.id,
            "name": content_type.name,
            "description": getattr(content_type, "description", ""),
            "default_word_count": getattr(content_type, "default_word_count", "1000"),
            "is_enabled": getattr(content_type, "is_enabled", True),
            "prompt_template": getattr(content_type, "prompt_template", ""),
            "output_format": getattr(content_type, "output_format", {}),
            "required_elements": getattr(content_type, "required_elements", {}),
            "optional_elements": getattr(content_type, "optional_elements", {}),
        }

    #
    # 文章风格相关方法
    #

    @classmethod
    def load_article_styles(cls) -> Dict[str, Any]:
        """从数据库加载所有文章风格

        Returns:
            Dict[str, Any]: 文章风格字典，键为风格名称
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.models.db.repository import article_style_repo

            # 获取所有文章风格
            styles = article_style_repo.get_all()
            return {style.name: style for style in styles}
        except Exception as e:
            logger.error(f"从数据库加载文章风格失败: {str(e)}")
            return {}

    @classmethod
    def get_article_style(cls, style_name: str) -> Optional[Any]:
        """获取指定名称的文章风格

        Args:
            style_name: 风格名称

        Returns:
            Optional[Any]: 文章风格对象
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.models.db.repository import article_style_repo

            # 获取文章风格
            return article_style_repo.get(style_name)
        except Exception as e:
            logger.error(f"获取文章风格失败: {str(e)}")
            return None

    @classmethod
    def save_article_style(cls, style: Any) -> bool:
        """保存文章风格到数据库

        Args:
            style: 文章风格对象

        Returns:
            bool: 是否成功保存
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.models.db.repository import article_style_repo

            # 转换为字典
            style_dict = cls._get_style_dict(style)

            # 检查是否已存在
            existing = article_style_repo.get(style.name)
            if existing:
                # 更新
                article_style_repo.update(style.name, style_dict)
                logger.info(f"已更新文章风格: {style.name}")
            else:
                # 创建
                article_style_repo.create(style_dict)
                logger.info(f"已创建文章风格: {style.name}")

            return True
        except Exception as e:
            logger.error(f"保存文章风格失败: {str(e)}")
            return False

    @staticmethod
    def _get_style_dict(style: Any) -> Dict[str, Any]:
        """将风格对象转换为字典

        Args:
            style: 风格对象

        Returns:
            Dict[str, Any]: 风格字典
        """
        if hasattr(style, "to_dict"):
            return style.to_dict()

        return {
            "name": style.name,
            "description": getattr(style, "description", ""),
            "is_enabled": getattr(style, "is_enabled", True),
            "tone": getattr(style, "tone", ""),
            "style_characteristics": getattr(style, "style_characteristics", {}),
            "language_preference": getattr(style, "language_preference", {}),
            "writing_format": getattr(style, "writing_format", {}),
            "prompt_template": getattr(style, "prompt_template", ""),
            "example": getattr(style, "example", ""),
        }

    #
    # 平台相关方法
    #

    @classmethod
    def load_platforms(cls) -> Dict[str, Any]:
        """从数据库加载所有平台配置

        Returns:
            Dict[str, Any]: 平台配置字典
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return {}

            # 导入仓库
            from core.models.db.repository import platform_repo

            # 获取所有平台
            platforms = platform_repo.get_all()
            return {platform.id: platform for platform in platforms}
        except Exception as e:
            logger.error(f"从数据库加载平台配置失败: {str(e)}")
            return {}

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Any]:
        """获取指定ID的平台配置

        Args:
            platform_id: 平台ID

        Returns:
            Optional[Any]: 平台配置对象
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return None

            # 导入仓库
            from core.models.db.repository import platform_repo

            # 获取平台
            return platform_repo.get(platform_id)
        except Exception as e:
            logger.error(f"获取平台配置失败: {str(e)}")
            return None

    @classmethod
    def save_platform(cls, platform: Any) -> bool:
        """保存平台配置到数据库

        Args:
            platform: 平台配置对象

        Returns:
            bool: 是否成功保存
        """
        try:
            # 初始化数据库
            if not cls.initialize():
                return False

            # 导入仓库
            from core.models.db.repository import platform_repo

            # 转换为字典
            platform_dict = cls._get_platform_dict(platform)

            # 检查是否已存在
            existing = platform_repo.get(platform.id)
            if existing:
                # 更新
                platform_repo.update(platform.id, platform_dict)
                logger.info(f"已更新平台配置: {platform.id}")
            else:
                # 创建
                platform_repo.create(platform_dict)
                logger.info(f"已创建平台配置: {platform.id}")

            return True
        except Exception as e:
            logger.error(f"保存平台配置失败: {str(e)}")
            return False

    @staticmethod
    def _get_platform_dict(platform: Any) -> Dict[str, Any]:
        """将平台对象转换为字典

        Args:
            platform: 平台对象

        Returns:
            Dict[str, Any]: 平台字典
        """
        if hasattr(platform, "to_dict"):
            return platform.to_dict()

        return {
            "id": platform.id,
            "name": platform.name,
            "description": getattr(platform, "description", ""),
            "is_enabled": getattr(platform, "is_enabled", True),
            "platform_type": getattr(platform, "platform_type", ""),
            "url": getattr(platform, "url", ""),
            "logo_url": getattr(platform, "logo_url", ""),
            "max_title_length": getattr(platform, "max_title_length", {}),
            "max_content_length": getattr(platform, "max_content_length", {}),
            "allowed_media_types": getattr(platform, "allowed_media_types", {}),
            "api_config": getattr(platform, "api_config", {}),
        }
