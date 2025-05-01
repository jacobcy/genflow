"""平台管理器

负责从配置文件加载平台配置并提供访问接口。
这是一个只读的配置管理器。
"""

from typing import Dict, List, Optional, Any, ClassVar
from loguru import logger
import os

# Import Pydantic model and loader
from core.models.platform.platform import Platform
from core.models.infra.json_loader import load_json_config, get_config_file_path

# Removed BaseManager import
# Removed platform_validator import
# Removed Article import

# No longer inherits from BaseManager
class PlatformManager:
    """平台管理器

    从 config/platforms/platforms.json 加载平台配置并提供访问接口。
    这是一个只读的配置管理器。
    """

    _platforms: ClassVar[Dict[str, Platform]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def ensure_initialized(cls) -> None:
        """确保管理器已初始化"""
        if not cls._initialized:
            cls.initialize()

    @classmethod
    def initialize(cls) -> None:
        """初始化平台管理器，从 JSON 文件加载数据"""
        if cls._initialized:
            return

        cls._load_platforms()
        cls._initialized = True
        logger.info(f"平台管理器初始化完成，加载了 {len(cls._platforms)} 个平台。")

    @classmethod
    def _load_platforms(cls) -> None:
        """从 core/models/platform/collection/ 目录加载平台数据"""
        cls._platforms = {}
        # Define the relative path to the collection directory
        collection_dir = os.path.join(os.path.dirname(__file__), 'collection')

        if not os.path.isdir(collection_dir):
            logger.error(f"平台配置目录不存在: {collection_dir}")
            return

        loaded_count = 0
        for filename in os.listdir(collection_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(collection_dir, filename)
                try:
                    # Use the json_loader utility for consistency, though direct open is fine too
                    platform_data = load_json_config(file_path)
                    if platform_data:
                        # Use the simplified Platform Pydantic model
                        platform = Platform(**platform_data)
                        # Use 'id' field from JSON as the key
                        if hasattr(platform, 'id') and platform.id:
                            cls._platforms[platform.id] = platform
                            loaded_count += 1
                        else:
                            logger.warning(f"平台文件 {filename} 数据缺少 'id' 字段，跳过。")
                    else:
                        logger.warning(f"无法加载或解析平台文件: {file_path}")
                except Exception as e:
                    logger.error(f"加载平台文件失败: {file_path}, 错误: {e}")

        logger.debug(f"从 {collection_dir} 成功加载 {loaded_count} 个平台配置。")

    @classmethod
    def get_platform(cls, platform_id: str) -> Optional[Platform]:
        """获取指定ID的平台配置

        Args:
            platform_id: 平台ID (e.g., 'wechat_mp')

        Returns:
            Optional[Platform]: 平台对象，不存在则返回None
        """
        cls.ensure_initialized()
        return cls._platforms.get(platform_id)

    @classmethod
    def get_platform_by_name(cls, name: str) -> Optional[Platform]:
        """根据平台名称获取平台配置 (大小写不敏感)

        Args:
            name: 平台名称 (e.g., '微信公众号')

        Returns:
            Optional[Platform]: 平台对象，不存在则返回None
        """
        cls.ensure_initialized()
        search_name = name.lower()
        for platform in cls._platforms.values():
            if platform.name.lower() == search_name:
                return platform
        return None

    @classmethod
    def get_all_platforms(cls) -> List[Platform]:
        """获取所有已加载的平台配置列表

        Returns:
            List[Platform]: 平台对象列表
        """
        cls.ensure_initialized()
        return list(cls._platforms.values())

    # Removed save_platform method
    # Removed validate_article method
    # Removed get_platform_constraints method

    # Add method to get default if needed, based on a predefined ID
    # For example, if 'default' is a valid platform ID in the config:
    # @classmethod
    # def get_default_platform(cls) -> Optional[Platform]:
    #     cls.ensure_initialized()
    #     return cls.get_platform('default')
